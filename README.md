# PDF Accessibility Toolkit

Convert scanned or inaccessible PDFs into Word documents with stronger accessibility support for higher-ed workflows.

## Choose Your Approach First

This project supports two ways to run the same conversion pipeline.

### Option A: Script-Based Workflow (Default)

Use terminal commands in this repository.

Best for:
- direct local control
- repeatable batch runs
- easier debugging and troubleshooting

### Option B: Codex Skill Workflow (Alternative)

Install the bundled skill so Codex can run the workflow from chat prompts.

Best for:
- prompt-driven usage in Codex
- teams already using Codex skills

Important:
- Both options still require a valid `MISTRAL_API_KEY`.
- Both options use the same underlying scripts and conversion logic.

## Shared Requirements (Both Options)

You need:
- Python 3.8+
- A Mistral API key
- Local file access to your PDFs

Create your `.env` file with:

```env
MISTRAL_API_KEY=your_key_here
```

`.env` lookup order (used by the scripts):
1. Path passed with `--env-file`
2. Input PDF folder (for example, `work/input/.env`)
3. Current working directory (for example, repo root)
4. Skill/script-local `.env`
5. Existing shell environment variable `MISTRAL_API_KEY`

Practical default:
- Put `.env` in the same folder where you run commands (often repo root), or in the input PDF folder.

## Option A (Default): Script-Based Install and Run

### 1. Get the repository

```bash
git clone https://github.com/Brehove/pdf-accessibility-toolkit.git
cd pdf-accessibility-toolkit
```

### 2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up API key

Get a key from [Mistral AI Console](https://console.mistral.ai/api-keys).

```bash
cp .env.example .env
# edit .env and set MISTRAL_API_KEY
```

### 4. Prepare input PDFs

```bash
mkdir -p work/input
# place PDF files in work/input
```

### 5. Run isolated batch conversion (recommended)

```bash
./convert_pdfs_isolated.sh work/input
```

What this does:
- Processes each PDF in its own folder (prevents image filename collisions)
- Runs OCR -> DOCX conversion -> table-header verification per file

### 6. Find outputs

Output root:
- `work/input/conversion_runs/`

Per-PDF output folder:
- `work/input/conversion_runs/<pdf-stem>/`

Typical files per PDF:
- `<name>.pdf` (copied source)
- `<name>.md`
- `<name>.docx`
- `<name>_accessible.docx`
- Extracted images (if present)

### Optional: Legacy shared-output flow (not recommended)

```bash
mkdir -p work/output
python3 scripts/mistral_ocr_batch.py --input-dir work/input --output-dir work/output
python3 scripts/md_to_accessible_docx.py work/output/*.md
```

Why not recommended:
- Image names can collide across documents in one shared folder.

## Option B: Codex Skill Install and Run

### 1. Install the skill package

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/codex/higher-ed-pdf-accessibility "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Or install directly from GitHub (recommended for clean/new-user testing):

```bash
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" python3 "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo Brehove/pdf-accessibility-toolkit --path skills/codex/higher-ed-pdf-accessibility
```

After installing, restart Codex so new skills are loaded.

Installed skill contents:
- `SKILL.md` (workflow instructions)
- `scripts/` (conversion scripts)
- `references/` (QA docs)
- `agents/` (support docs)

### 2. Keep using `.env` and dependencies

Even with skills, you still need:
- Python dependencies available in the runtime environment
- `MISTRAL_API_KEY` via `.env`, `--env-file`, or shell environment
- Input PDFs in a folder you specify

### 3. Run via Codex prompt

In Codex, ask to use `higher-ed-pdf-accessibility` on your target folder.

Example intent:
- “Use the accessibility skill to batch convert PDFs in `work/input`.”

### 4. What the rest of this repo is still for

Even if you use only the installed skill package, the root repo is still useful for:
- local script testing
- troubleshooting and debugging
- manual QA guidance in `docs/`

## What Each Script Does

- `scripts/mistral_ocr_batch.py`
  - Converts PDF pages to Markdown via Mistral OCR
- `scripts/md_to_accessible_docx.py`
  - Converts Markdown structure into accessible Word structure
- `scripts/fix_docx_table_headers.py`
  - Ensures table headers are marked for assistive technologies
- `convert_pdfs_isolated.sh`
  - Orchestrates the full pipeline one PDF per folder

## Accessibility QA (Required)

Automated conversion is not sufficient for publishing to students. Documents should be manually verified.

Use:
- `docs/qa-checklist.md`
- `docs/alt-text-guidance.md`
- `docs/long-document-handling.md`

Minimum manual checks:
- Heading hierarchy is logical
- Table headers are correct
- Alt text quality is meaningful
- Reading order is understandable

## Troubleshooting

Common issues:
- `MISTRAL_API_KEY environment variable not set`
  - Verify `.env` location or pass `--env-file`.
- `No PDFs found`
  - Confirm files end in `.pdf`/`.PDF` and are in the expected input folder.
- API/network failures
  - Re-run failed files individually; long documents may need retries.

## Notes and Limits

- OCR quality controls output quality.
- Complex layouts (dense math, multi-column pages, complex tables) still need manual review.
- This tool accelerates remediation; it does not replace human accessibility review.

## License

MIT. See `LICENSE`.
