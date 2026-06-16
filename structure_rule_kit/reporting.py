from __future__ import annotations


def issue(severity: str, message: str, file: str = "", section: str = "") -> dict:
    return {
        "severity": severity,
        "message": message,
        "file": file,
        "section": section,
    }


def issue_messages(issues: list[dict], severity: str) -> list[str]:
    return [item["message"] for item in issues if item.get("severity") == severity]
