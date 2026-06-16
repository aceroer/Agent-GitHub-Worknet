from __future__ import annotations

from pathlib import Path


DEFAULT_IGNORE_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
    ".venv",
}

SOURCE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".rs", ".go", ".java", ".c", ".cpp", ".h", ".hpp"}
TEST_HINTS = ("test", "tests", "spec")
DOC_SUFFIXES = {".md", ".rst", ".txt"}
CONFIG_NAMES = {"pyproject.toml", "package.json", "tsconfig.json", "Cargo.toml", "go.mod", "Makefile"}
CONFIG_SUFFIXES = {".toml", ".yaml", ".yml", ".json", ".ini", ".cfg"}
GENERATED_NAMES = {
    "STRUCTURE_CONTEXT.md",
    "STRUCTURE_CONTEXT_PACK.md",
    "STRUCTURE_CONTEXT_PRUNED.md",
    "STRUCTURE_HANDOFF.md",
}
GENERATED_STRUCTURE_NAMES = {
    "decision_log.md",
    "mcp_manifest.json",
    "rag_index.json",
    "repo_map.md",
    "verification_log.md",
}


def _category(path: Path) -> str:
    parts = {part.lower() for part in path.parts}
    name = path.name
    suffix = path.suffix
    if name in GENERATED_NAMES or (path.parts and path.parts[0] == "structure" and name in GENERATED_STRUCTURE_NAMES):
        return "generated"
    if any(hint in parts or hint in name.lower() for hint in TEST_HINTS):
        return "tests"
    if suffix in SOURCE_SUFFIXES:
        return "source"
    if suffix in DOC_SUFFIXES:
        return "docs"
    if name in CONFIG_NAMES or suffix in CONFIG_SUFFIXES:
        return "config"
    return "other"


def scan_repo_map(path: str = ".", output: str = "structure/repo_map.md", max_files: int = 240) -> dict:
    root = Path(path)
    buckets = {"source": [], "tests": [], "docs": [], "config": [], "generated": [], "other": []}

    for target in sorted(root.rglob("*")):
        current_count = sum(len(items) for items in buckets.values())
        if current_count >= max_files:
            break
        if target.is_dir():
            continue
        relative = target.relative_to(root)
        if any(part in DEFAULT_IGNORE_DIRS for part in relative.parts):
            continue
        buckets[_category(relative)].append(str(relative))

    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    counts = {category: len(files) for category, files in buckets.items()}
    chunks = ["# Repository Map", "", "## Summary", ""]
    for category, count in counts.items():
        chunks.append(f"- {category}: {count}")
    chunks.append("")
    for category, files in buckets.items():
        chunks.append(f"## {category.title()}")
        chunks.append("")
        if files:
            chunks.extend(f"- `{item}`" for item in files)
        else:
            chunks.append("- Not found.")
        chunks.append("")
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return {"output": str(output_path), "files": sum(len(items) for items in buckets.values()), "counts": counts}
