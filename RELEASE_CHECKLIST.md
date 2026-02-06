# Release Checklist

Use this before publishing or cutting a new release.

## 1) Pre-publish safety checks

- [ ] Confirm you are in the clean export folder:

```bash
pwd
# expected: .../pdf-accessibility-toolkit
```

- [ ] Confirm no secrets are committed:

```bash
grep -R -n "MISTRAL_API_KEY\|sk-" . || true
```

- [ ] Confirm `.env` is not tracked and `.env.example` exists.
- [ ] Confirm no private/source course files are included (`.pdf`, `.docx`, `.pptx` unless intentionally added as examples).

## 2) Functional smoke checks

- [ ] CLI help checks:

```bash
uv run --with mistralai --with python-dotenv python3 scripts/mistral_ocr_batch.py -h
uv run --with python-docx --with python-dotenv --with mistralai python3 scripts/md_to_accessible_docx.py -h
uv run --with python-docx python3 scripts/fix_docx_table_headers.py -h
```

- [ ] Optional end-to-end test with a small sample PDF (non-sensitive).
- [ ] Validate output quality using `docs/qa-checklist.md`.

## 3) Repository quality

- [ ] `README.md` is accurate and runnable by a new user.
- [ ] `LICENSE` present.
- [ ] `CONTRIBUTING.md` present.
- [ ] `requirements.txt` up to date.
- [ ] Optional skill docs under `skills/` are accurate.

## 4) GitHub publish steps

```bash
git init
git add .
git commit -m "Initial public release"
```

Then create an empty GitHub repo and run:

```bash
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## 5) First tagged release

- [ ] Create tag:

```bash
git tag -a v0.1.0 -m "Initial public release"
git push origin v0.1.0
```

- [ ] Draft GitHub Release notes with:
- Overview of OCR -> Markdown -> DOCX workflow
- Known limitations (complex tables/layout/math)
- QA requirement reminder
- Skill bundle is optional

## 6) Post-release housekeeping

- [ ] Open one issue template for bug reports.
- [ ] Open one issue template for enhancement requests.
- [ ] Add at least one milestone (for example: `v0.2.0`).
