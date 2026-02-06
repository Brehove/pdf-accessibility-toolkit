# Contributing

## Scope

This project focuses on higher-ed PDF remediation:
- OCR PDF -> Markdown
- Markdown -> accessible DOCX
- QA guidance and repeatable workflows

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Contribution guidelines

- Keep changes cross-platform and avoid machine-specific paths.
- Do not commit API keys or real student/institutional documents.
- Add/update docs when changing CLI behavior.
- Prefer deterministic output behavior over hidden heuristics.

## Testing expectations

Before opening a PR:
- Run script help checks (`-h`) for changed CLIs.
- Run one small end-to-end test on a sample PDF.
- Verify output with `docs/qa-checklist.md`.
