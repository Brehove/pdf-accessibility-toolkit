# Long Document Handling

Use this for long PDFs (for example: large packets, dissertations, multi-chapter readings).

## Processing strategy
1. Process one PDF at a time.
2. Review generated Markdown before DOCX conversion.
3. Convert to DOCX and run QA before moving to the next file.

## Failure isolation
- If OCR fails on one file, continue with remaining files.
- Re-run only failed files after correcting API/network/input issues.
- Keep intermediate Markdown so reruns do not lose manual cleanup work.

## Practical tips
- Keep source PDFs in a dedicated per-course folder.
- Use stable naming (`COURSE_term_topic.pdf`) to simplify tracking.
- For image-heavy content, spend extra QA time on alt text quality.

## Manual review triggers
- Dense math pages
- Complex multi-level tables
- Multi-column page layouts
- Figure captions detached from figures
