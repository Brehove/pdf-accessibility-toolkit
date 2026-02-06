# Skill Bundle

This folder contains an optional Codex skill package.

## Install

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex/higher-ed-pdf-accessibility "${CODEX_HOME:-$HOME/.codex}/skills/"
```

The skill can then be referenced as `higher-ed-pdf-accessibility`.

## Notes

- The core toolkit in `scripts/` works without any skill system.
- Keep this folder optional for users who only need the Python CLI workflow.
