---
name: "higher-ed-pdf-accessibility"
description: "Use when the user wants to remediate higher-education PDFs into accessible formats (PDF to Markdown to accessible DOCX), including course readings, handouts, and image-heavy files."
---

# Higher-Ed PDF Accessibility

## When to use
- The user asks to make PDFs accessible for students, faculty, disability services, or LMS upload.
- The files include scanned text, headings, lists, tables, and images.
- The user needs a repeatable PDF -> Markdown -> accessible DOCX workflow.

## Scope
- Primary workflow: OCR PDF -> Markdown -> accessible DOCX.
- Supports batch processing for mixed short and long files.
- Keeps deterministic conversion logic in bundled scripts.

## Preflight
1. Work from the folder containing the target PDFs.
2. Prefer `uv run` so dependencies are injected automatically per run.
3. If `uv` is unavailable, install dependencies manually:
```bash
python3 -m pip install mistralai python-docx python-dotenv
```
4. `MISTRAL_API_KEY` is loaded automatically from `.env` locations in this order:
- `--env-file` (if provided)
- input folder `.env`
- current working folder `.env`
- skill-local `.env`
- fallback to shell environment variable

## Runbook
Set the skill directory once:
```bash
SKILL_DIR="${CODEX_HOME:-$HOME/.codex}/skills/higher-ed-pdf-accessibility"
```

Run OCR on PDFs in current folder:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/mistral_ocr_batch.py" --input-dir . --output-dir .
```

Optional: point to a specific `.env`:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/mistral_ocr_batch.py" --input-dir . --output-dir . --env-file "/path/to/.env"
```

Convert Markdown files to accessible DOCX:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/md_to_accessible_docx.py" *.md
```

Optional: point DOCX conversion to a specific `.env`:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/md_to_accessible_docx.py" *.md --env-file "/path/to/.env"
```

Optional: disable auto alt-text generation:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/md_to_accessible_docx.py" *.md --no-auto-alt
```

Optional: preserve original OCR page boundaries:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/md_to_accessible_docx.py" *.md --preserve-page-breaks
```

Optional: disable first-page author side-by-side normalization:
```bash
uv run --with mistralai --with python-dotenv --with python-docx \
  python3 "$SKILL_DIR/scripts/md_to_accessible_docx.py" *.md --no-author-grid
```

Optional: repair table headers in existing DOCX files:
```bash
uv run --with python-docx \
  python3 "$SKILL_DIR/scripts/fix_docx_table_headers.py" *.docx --verify
```

## Long document handling
- For very long PDFs, process one file at a time to reduce failures and simplify QA.
- Use the guidance in `references/long-document-handling.md` before reruns.

## QA requirements
- Always run a post-conversion quality pass for headings, table headers, image alt text, and reading order.
- Use `references/qa-checklist.md`.
- Use `references/alt-text-guidance.md` when generated alt text is weak.

## Output expectations
- Each input PDF should produce:
  - `<name>.md`
  - `<name>.docx`
  - extracted images under `extracted_images/` when needed
- Report failed files separately and continue processing remaining files.
