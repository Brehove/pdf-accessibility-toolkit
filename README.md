# PDF Accessibility Toolkit

Convert scanned or inaccessible PDFs into Word documents with stronger accessibility support for higher-ed workflows.

## What this includes

- OCR PDF -> Markdown (`scripts/mistral_ocr_batch.py`)
- Markdown -> accessible DOCX (`scripts/md_to_accessible_docx.py`)
- Table-header repair for existing DOCX (`scripts/fix_docx_table_headers.py`)
- QA guidance (`docs/`)
- Optional Codex skill bundle (`skills/codex/higher-ed-pdf-accessibility/`)

## Quick Start

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set your API key

Get a key from [Mistral AI Console](https://console.mistral.ai/api-keys).

```bash
cp .env.example .env
# edit .env and set MISTRAL_API_KEY
```

### 3. Prepare input/output folders

```bash
mkdir -p work/input work/output
# place PDF files in work/input
```

### 4. Run OCR (PDF -> Markdown + images)

```bash
python3 scripts/mistral_ocr_batch.py --input-dir work/input --output-dir work/output
```

### 5. Convert Markdown to DOCX

```bash
python3 scripts/md_to_accessible_docx.py work/output/*.md
```

Optional formatting controls:

```bash
# Preserve original OCR page boundaries in Word output
python3 scripts/md_to_accessible_docx.py work/output/*.md --preserve-page-breaks

# Disable first-page author side-by-side normalization
python3 scripts/md_to_accessible_docx.py work/output/*.md --no-author-grid
```

## Accessibility QA (Required)

Automated conversion is not sufficient for publishing to students.

Use:
- `docs/qa-checklist.md`
- `docs/alt-text-guidance.md`
- `docs/long-document-handling.md`

## Optional: Use as a Codex Skill

This repo includes an optional skill package in:
- `skills/codex/higher-ed-pdf-accessibility/`

To install into Codex:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/codex/higher-ed-pdf-accessibility "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Then use the skill name `higher-ed-pdf-accessibility` in your Codex workflow.

## Notes and limits

- OCR quality controls output quality.
- Complex layouts (dense math, multi-column pages, complex tables) still need manual review.
- API/network failures should be retried file-by-file for long documents.

## License

MIT. See `LICENSE`.
