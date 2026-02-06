#!/usr/bin/env python3
"""
Batch OCR processor using Mistral AI
Converts all PDFs in a folder to Markdown files with images extracted.
"""

import os
import argparse
import base64
import re
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from mistralai import Mistral

IMAGES_SUBFOLDER = "extracted_images"  # Where to save extracted images

IMAGE_REF_PATTERN = re.compile(r'!\[(.*?)\]\((.*?)\)')

def get_client():
    """Initialize Mistral client."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set")
    return Mistral(api_key=api_key)

def split_markdown_link_target(target: str) -> str:
    """Extract the path part from a markdown link target, stripping any title."""
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        return target[1:-1].strip()
    # Remove optional title at the end: path "title"
    match = re.match(r'(.+?)\s+["\'].*["\']$', target)
    if match:
        return match.group(1).strip()
    return target

def normalize_image_ref_path(path: str) -> str:
    """Normalize a markdown image path to a safe relative path."""
    path = path.strip().replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    if path.startswith(".\\"):
        path = path[2:]
    try:
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj.name
    except Exception:
        return path
    return path

def is_probably_url(path: str) -> bool:
    """Return True if the path looks like a URL or data URI."""
    lower = path.lower()
    return lower.startswith("http://") or lower.startswith("https://") or lower.startswith("data:")

def extract_image_refs(markdown: str) -> list[dict]:
    """Extract image references from markdown in document order."""
    refs = []
    for match in IMAGE_REF_PATTERN.finditer(markdown):
        alt_text = match.group(1).strip()
        target = match.group(2).strip()
        path = split_markdown_link_target(target)
        path = normalize_image_ref_path(path)
        if not path or is_probably_url(path):
            continue
        refs.append({"alt": alt_text, "path": path})
    return refs

def decode_image_bytes(image_base64: str) -> tuple[bytes, str]:
    """Decode base64 image and infer extension."""
    img_bytes = base64.b64decode(image_base64)
    jpeg_start = img_bytes.find(b'\xff\xd8\xff')
    png_start = img_bytes.find(b'\x89PNG')

    if jpeg_start >= 0:
        return img_bytes[jpeg_start:], '.jpg'
    if png_start >= 0:
        return img_bytes[png_start:], '.png'
    return img_bytes, '.jpg'

def process_pdf(client, pdf_path: Path) -> tuple[str, list[tuple[str, bytes]]]:
    """
    Process a single PDF and return markdown content and images.
    Returns: (markdown_text, list of (image_filename, image_bytes))
    """
    # Read and encode PDF as data URI
    with open(pdf_path, "rb") as f:
        encoded_pdf = base64.standard_b64encode(f.read()).decode("utf-8")

    # Call Mistral OCR using data URI format
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{encoded_pdf}"
        },
        include_image_base64=True
    )

    # Collect markdown and images
    markdown_pages = []
    images = []
    image_counter = 1

    for page_num, page in enumerate(response.pages, 1):
        page_markdown = page.markdown
        image_refs = extract_image_refs(page_markdown)
        ref_index = 0

        # Extract images if present
        if hasattr(page, 'images') and page.images:
            for img in page.images:
                if hasattr(img, 'image_base64') and img.image_base64:
                    # Decode image
                    img_bytes, ext = decode_image_bytes(img.image_base64)

                    # Map to existing markdown image refs if present
                    if image_refs and ref_index < len(image_refs):
                        target_path = image_refs[ref_index]["path"]
                        ref_index += 1
                        if target_path:
                            images.append((target_path, img_bytes))
                            continue

                    # Fallback: generate image filename and append reference
                    img_filename = f"{pdf_path.stem}_img_{image_counter:03d}{ext}"
                    image_counter += 1
                    rel_path = f"{IMAGES_SUBFOLDER}/{img_filename}"
                    images.append((rel_path, img_bytes))

                    img_ref = f"![{img_filename}]({rel_path})"
                    page_markdown += f"\n\n{img_ref}"

        markdown_pages.append(f"<!-- Page {page_num} -->\n\n{page_markdown}")

    full_markdown = "\n\n---\n\n".join(markdown_pages)
    return full_markdown, images

def save_images(images: list[tuple[str, bytes]], output_folder: Path):
    """Save extracted images to disk."""
    if not images:
        return
    for rel_path, img_bytes in images:
        rel_path = normalize_image_ref_path(rel_path)
        img_path = output_folder / rel_path
        img_path.parent.mkdir(parents=True, exist_ok=True)
        with open(img_path, "wb") as f:
            f.write(img_bytes)
        print(f"    Saved image: {img_path.name}")


def load_env_context(input_dir: Path, env_file: Optional[str] = None):
    """Load MISTRAL_API_KEY from likely .env locations."""
    script_dir = Path(__file__).resolve().parent
    candidates = []
    if env_file:
        candidates.append(Path(env_file).expanduser())
    candidates.extend([
        input_dir / ".env",
        Path.cwd() / ".env",
        script_dir / ".env",
        script_dir.parent / ".env",
    ])

    loaded = []
    seen = set()
    for candidate in candidates:
        candidate = candidate.expanduser()
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            loaded.append(candidate)

    if loaded:
        print(f"Loaded .env: {loaded[0]}")
    else:
        print("No .env file found in default locations; using shell environment only.")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch OCR PDFs to Markdown with extracted images",
    )
    parser.add_argument(
        "--input-dir",
        default=".",
        help="Folder containing PDFs to process (default: current working directory)",
    )
    parser.add_argument(
        "--output-dir",
        help="Folder for output .md files and images (default: same as input-dir)",
    )
    parser.add_argument(
        "--env-file",
        help="Optional path to .env containing MISTRAL_API_KEY",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else input_dir

    load_env_context(input_dir, args.env_file)

    print("=" * 60)
    print("Mistral OCR Batch Processor")
    print("=" * 60)
    print(f"Input folder: {input_dir}")
    print(f"Output folder: {output_dir}")

    # Initialize client
    try:
        client = get_client()
        print("✓ Mistral client initialized")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nSet your API key with:")
        print("  export MISTRAL_API_KEY='your_key_here'")
        return

    # Find all PDFs
    if not input_dir.exists():
        print(f"\nInput folder not found: {input_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(list(input_dir.glob("*.pdf")) + list(input_dir.glob("*.PDF")))

    if not pdf_files:
        print(f"\nNo PDF files found in: {input_dir}")
        return

    print(f"\nFound {len(pdf_files)} PDF(s) to process:\n")

    # Process each PDF
    successful = 0
    failed = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing: {pdf_path.name}")

        try:
            # Run OCR
            markdown_content, images = process_pdf(client, pdf_path)

            # Save markdown
            md_path = output_dir / f"{pdf_path.stem}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"    ✓ Created: {md_path.name}")

            # Save images
            if images:
                save_images(images, output_dir)
                print(f"    ✓ Extracted {len(images)} image(s)")

            successful += 1

        except Exception as e:
            print(f"    ✗ Failed: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"Complete! Processed {successful} of {len(pdf_files)} PDFs")
    if failed:
        print(f"  ({failed} failed)")
    print("=" * 60)

if __name__ == "__main__":
    main()
