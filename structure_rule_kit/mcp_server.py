from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .context_pack import build_context_pack
from .summary import summarize_structure


RESOURCE_NAMES = [
    "STRUCTURE_RULE.md",
    "STRUCTURE_AGENT_BRIEF.md",
    "STRUCTURE_CONTEXT_PRUNED.md",
    "STRUCTURE_CONTEXT_PACK.md",
]

SERVER_INFO = {"name": "agent-github-worknet", "version": "1.5.0"}
PROTOCOL_VERSION = "2024-11-05"


def _safe_target(root: Path, relative: str) -> Path:
    base = root.resolve()
    target = (base / relative).resolve()
    if target != base and base not in target.parents:
        raise ValueError("Resource escapes repository root")
    if not target.exists() or not target.is_file():
        raise FileNotFoundError(relative)
    return target


def list_resource_paths(root: Path) -> list[Path]:
    paths = [root / name for name in RESOURCE_NAMES]
    structure_dir = root / "structure"
    if structure_dir.exists():
        paths.extend(sorted(structure_dir.glob("*.md")))
        paths.extend(sorted(structure_dir.glob("*.json")))
    return [path for path in paths if path.exists() and path.is_file()]


def list_resources(path: str = ".") -> list[dict]:
    root = Path(path).resolve()
    resources = []
    for resource_path in list_resource_paths(root):
        relative = resource_path.relative_to(root)
        resources.append(
            {
                "uri": f"structure-rule://{relative}",
                "name": str(relative),
                "mimeType": "application/json" if resource_path.suffix == ".json" else "text/markdown",
                "description": f"Agent GitHub Worknet resource: {relative}",
            }
        )
    return resources


def read_resource(path: str = ".", uri: str = "") -> dict:
    root = Path(path).resolve()
    prefix = "structure-rule://"
    if not uri.startswith(prefix):
        raise ValueError(f"Unsupported URI: {uri}")
    target = _safe_target(root, uri[len(prefix) :])
    mime_type = "application/json" if target.suffix == ".json" else "text/markdown"
    return {"uri": uri, "mimeType": mime_type, "text": target.read_text(encoding="utf-8")}


def list_tools() -> list[dict]:
    return [
        {
            "name": "structure_rule_summary",
            "description": "Return a compact Agent GitHub Worknet project summary.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "structure_rule_context_pack",
            "description": "Build and return a bounded structure context pack.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "max_chars_per_file": {"type": "integer", "minimum": 200, "maximum": 20000},
                },
                "additionalProperties": False,
            },
        },
    ]


def call_tool(path: str = ".", name: str = "", arguments: dict | None = None) -> dict:
    arguments = arguments or {}
    if name == "structure_rule_summary":
        payload = summarize_structure(path)
        return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}
    if name == "structure_rule_context_pack":
        report = build_context_pack(path, max_chars_per_file=int(arguments.get("max_chars_per_file", 2400)))
        text = Path(report["output"]).read_text(encoding="utf-8")
        return {"content": [{"type": "text", "text": text}]}
    raise ValueError(f"Unknown tool: {name}")


def mcp_result(path: str, method: str, params: dict | None = None) -> dict:
    params = params or {}
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"resources": {}, "tools": {}},
            "serverInfo": SERVER_INFO,
        }
    if method == "notifications/initialized":
        return {}
    if method == "resources/list":
        return {"resources": list_resources(path)}
    if method == "resources/read":
        resource = read_resource(path, params.get("uri", ""))
        return {
            "contents": [
                {
                    "uri": resource["uri"],
                    "mimeType": resource["mimeType"],
                    "text": resource["text"],
                }
            ]
        }
    if method == "tools/list":
        return {"tools": list_tools()}
    if method == "tools/call":
        return call_tool(path, name=params.get("name", ""), arguments=params.get("arguments", {}))
    raise ValueError(f"Unsupported method: {method}")


def handle_jsonrpc(path: str, payload: dict) -> dict | None:
    request_id = payload.get("id")
    method = payload.get("method", "")
    try:
        result = mcp_result(path, method, payload.get("params", {}))
    except Exception as exc:  # MCP servers should return JSON-RPC errors, not tracebacks.
        if request_id is None:
            return None
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": str(exc)},
        }
    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def run_server(path: str = ".", request: str = "") -> dict:
    payload = json.loads(request) if request else {"method": "resources/list"}
    if payload.get("jsonrpc") == "2.0":
        response = handle_jsonrpc(path, payload)
        return response or {}
    method = payload.get("method")
    if method == "resources/list":
        return {"resources": list_resources(path)}
    if method == "resources/read":
        uri = payload.get("params", {}).get("uri", "")
        return read_resource(path, uri)
    if method == "tools/list":
        return {"tools": list_tools()}
    if method == "tools/call":
        params = payload.get("params", {})
        return call_tool(path, name=params.get("name", ""), arguments=params.get("arguments", {}))
    return {"error": f"Unsupported method: {method}"}


def run_stdio_server(path: str = ".") -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            response = handle_jsonrpc(path, payload)
        except Exception as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            print(json.dumps(response), flush=True)


def run_http_server(path: str = ".", host: str = "127.0.0.1", port: int = 8765) -> None:
    root = str(Path(path).resolve())

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(body)
                response = handle_jsonrpc(root, payload) or {"jsonrpc": "2.0", "id": payload.get("id"), "result": {}}
                status = 200
            except Exception as exc:
                response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
                status = 400
            data = json.dumps(response).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *args: Any) -> None:
            return

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Agent GitHub Worknet MCP HTTP server listening on http://{host}:{port}", file=sys.stderr)
    server.serve_forever()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="structure-rule-mcp-server")
    parser.add_argument("--path", default=".")
    parser.add_argument("--request", default="")
    parser.add_argument("--stdio", action="store_true")
    parser.add_argument("--http", action="store_true")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if args.stdio:
        run_stdio_server(args.path)
        return 0
    if args.http:
        run_http_server(args.path, host=args.host, port=args.port)
        return 0
    print(json.dumps(run_server(args.path, args.request), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
