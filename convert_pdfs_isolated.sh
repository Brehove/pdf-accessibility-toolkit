#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  ./convert_pdfs_isolated.sh [pdf_dir] [output_root] [--env-file /path/to/.env]

Defaults:
  pdf_dir:     current directory
  output_root: <pdf_dir>/conversion_runs

Behavior:
  - Processes each PDF in its own folder: <output_root>/<pdf-stem>/
  - Runs OCR -> Markdown -> DOCX -> table-header verify per file
  - Continues on failures and prints a summary at the end
EOF
}

PDF_DIR="."
OUTPUT_ROOT=""
ENV_FILE=""

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env-file)
      [[ $# -ge 2 ]] || { echo "Missing value for --env-file" >&2; exit 2; }
      ENV_FILE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

if [[ ${#POSITIONAL[@]} -ge 1 ]]; then
  PDF_DIR="${POSITIONAL[0]}"
fi
if [[ ${#POSITIONAL[@]} -ge 2 ]]; then
  OUTPUT_ROOT="${POSITIONAL[1]}"
fi
if [[ ${#POSITIONAL[@]} -gt 2 ]]; then
  echo "Too many positional arguments." >&2
  usage
  exit 2
fi

PDF_DIR="$(cd "$PDF_DIR" && pwd)"
if [[ -z "$OUTPUT_ROOT" ]]; then
  OUTPUT_ROOT="$PDF_DIR/conversion_runs"
fi
mkdir -p "$OUTPUT_ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OCR_SCRIPT="$SCRIPT_DIR/scripts/mistral_ocr_batch.py"
DOCX_SCRIPT="$SCRIPT_DIR/scripts/md_to_accessible_docx.py"
TABLE_SCRIPT="$SCRIPT_DIR/scripts/fix_docx_table_headers.py"

if [[ ! -f "$OCR_SCRIPT" || ! -f "$DOCX_SCRIPT" || ! -f "$TABLE_SCRIPT" ]]; then
  echo "Required scripts not found next to convert_pdfs_isolated.sh" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required for this runner. Install uv or run the scripts manually." >&2
  exit 1
fi

shopt -s nullglob
pdfs=( "$PDF_DIR"/*.pdf "$PDF_DIR"/*.PDF )

if [[ ${#pdfs[@]} -eq 0 ]]; then
  echo "No PDFs found in: $PDF_DIR"
  exit 0
fi

echo "Input directory:  $PDF_DIR"
echo "Output root:      $OUTPUT_ROOT"
echo "PDF count:        ${#pdfs[@]}"

ok=0
fail=0

for pdf in "${pdfs[@]}"; do
  name="$(basename "$pdf")"
  stem="${name%.*}"
  run_dir="$OUTPUT_ROOT/$stem"

  echo
  echo "============================================================"
  echo "Processing: $name"
  echo "Run folder: $run_dir"
  echo "============================================================"

  rm -rf "$run_dir"
  mkdir -p "$run_dir"
  cp -f "$pdf" "$run_dir/$name"

  if [[ -n "$ENV_FILE" ]]; then
    if ! uv run --with mistralai --with python-dotenv --with python-docx \
        python3 "$OCR_SCRIPT" --input-dir "$run_dir" --output-dir "$run_dir" --env-file "$ENV_FILE"; then
      echo "Failed OCR: $name" >&2
      ((fail+=1))
      continue
    fi
  else
    if ! uv run --with mistralai --with python-dotenv --with python-docx \
        python3 "$OCR_SCRIPT" --input-dir "$run_dir" --output-dir "$run_dir"; then
      echo "Failed OCR: $name" >&2
      ((fail+=1))
      continue
    fi
  fi

  if [[ -n "$ENV_FILE" ]]; then
    if ! uv run --with mistralai --with python-dotenv --with python-docx \
        python3 "$DOCX_SCRIPT" "$run_dir"/*.md --env-file "$ENV_FILE"; then
      echo "Failed DOCX conversion: $name" >&2
      ((fail+=1))
      continue
    fi
  else
    if ! uv run --with mistralai --with python-dotenv --with python-docx \
        python3 "$DOCX_SCRIPT" "$run_dir"/*.md; then
      echo "Failed DOCX conversion: $name" >&2
      ((fail+=1))
      continue
    fi
  fi

  if ! uv run --with python-docx \
      python3 "$TABLE_SCRIPT" "$run_dir"/*.docx --verify; then
    echo "Table header verify failed: $name" >&2
    ((fail+=1))
    continue
  fi

  ((ok+=1))
done

echo
echo "============================================================"
echo "Complete"
echo "Succeeded: $ok"
echo "Failed:    $fail"
echo "Output:    $OUTPUT_ROOT"
echo "============================================================"
