"""
PDF text extraction for rulebook component analysis.
"""

import pdfplumber
import re


def extract_text_from_pdf(pdf_file, max_pages=50) -> str:
    """Extract text from uploaded PDF file.

    Args:
        pdf_file: Streamlit UploadedFile object
        max_pages: Maximum number of pages to process (default: 50)

    Returns:
        str: Extracted text from all pages (up to max_pages)

    Raises:
        Exception: If PDF cannot be read or is corrupted
    """
    try:
        all_text = []

        # Use pdfplumber to extract text
        with pdfplumber.open(pdf_file) as pdf:
            # Limit pages to prevent timeout
            num_pages = min(len(pdf.pages), max_pages)

            for page_num in range(num_pages):
                page = pdf.pages[page_num]
                text = page.extract_text()

                if text:
                    all_text.append(text)

        # Combine all page text
        combined_text = "\n\n".join(all_text)

        # Clean text (remove excessive whitespace)
        combined_text = re.sub(r'\n{3,}', '\n\n', combined_text)  # Max 2 newlines
        combined_text = re.sub(r' {2,}', ' ', combined_text)  # Max 1 space

        if not combined_text.strip():
            raise Exception("No text could be extracted from the PDF. It may be image-based or empty.")

        return combined_text.strip()

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
