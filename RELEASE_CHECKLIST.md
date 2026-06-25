# Release Checklist

## Preflight

- Confirm `pyproject.toml` version matches README current stable version.
- Confirm roadmap and protocol docs mention the release scope.
- Run `python3 -m py_compile structure_rule_kit/*.py tests/*.py`.
- Run `python -m pytest`.
- Run `ruff check .` when dev dependencies are installed.
- Run `mypy structure_rule_kit` when dev dependencies are installed.
- Run `python -m build`.

## Safety

- Confirm remote-write commands still require `--apply`.
- Confirm model live calls still require capability tokens.
- Confirm governance token expiry and revocation behavior.
- Confirm sandbox checks block symlink escapes.
- Confirm MCP server exposes only repository resources.

## GitHub

- Commit intentional changes only.
- Tag the release as `vX.Y.Z`.
- Push `main` and the tag.
- Check GitHub Actions status after push.

## Notes

- Record any skipped check and why.
- Keep generated caches, virtual environments, and local lock files out of the release unless intentionally tracked.
