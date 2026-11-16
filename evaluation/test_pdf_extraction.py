
import sys
import fitz
from pathlib import Path


def extract_with_blocks(page):
    blocks = page.get_text("blocks")

    page_blocks = []

    for block in blocks:
        x0, y0, x1, y1, text = block[:5]

        if text.strip():
            page_blocks.append({
                "x": x0,
                "y": y0,
                "text": text.strip()
            })

    page_blocks.sort(
        key=lambda block: (
            round(block["y"], 1),
            block["x"]
        )
    )

    return "\n".join(
        block["text"]
        for block in page_blocks
    )


def main():

    if len(sys.argv) < 2:
        print("Usage: python evaluation/test_pdf_extraction.py <pdf_path>")
        return

    pdf_path = Path(sys.argv[1])

    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return

    with fitz.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf, start=1):

            methods = {
                "TEXT_DEFAULT": page.get_text("text"),
                "TEXT_SORTED": page.get_text("text", sort=True),
                "BLOCKS_CURRENT": extract_with_blocks(page)
            }

            for method_name, extracted_text in methods.items():

                output_path = Path("evaluation") / (
                    f"page_{page_number}_{method_name}.txt"
                )

                output_path.write_text(
                    extracted_text,
                    encoding="utf-8"
                )

                print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
