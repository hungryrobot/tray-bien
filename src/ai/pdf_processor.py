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
            # Check if PDF contains images (scanned/image-based)
            has_images = False
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages[:5]:  # Check first 5 pages
                        if page.images:
                            has_images = True
                            break
            except:
                pass

            if has_images:
                raise Exception(
                    "This PDF appears to be scanned or image-based and requires OCR (Optical Character Recognition) "
                    "to extract text. Please use a digital PDF with selectable text, or add components manually."
                )
            else:
                raise Exception(
                    "No text could be extracted from this PDF. It may be empty, corrupted, or in an unsupported format. "
                    "Please try a different PDF or add components manually."
                )

        return combined_text.strip()

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
