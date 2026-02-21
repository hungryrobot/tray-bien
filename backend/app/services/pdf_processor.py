"""
PDF text extraction for rulebook component analysis.
"""

import pdfplumber
import re


def extract_text_from_pdf(pdf_file, max_pages=15) -> str:
    """Extract text from uploaded PDF file.

    Args:
        pdf_file: io.BytesIO object or file-like object
        max_pages: Maximum number of pages to process (default: 15, component lists can span many pages)

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

            # Diagnostic logging
            print(f"📄 PDF has {len(pdf.pages)} total pages, extracting first {num_pages} pages")
            if len(pdf.pages) > max_pages:
                print(f"⚠️  WARNING: PDF has MORE pages than limit! Component list may be cut off.")

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
                # Attempt OCR extraction for image-based PDFs
                try:
                    combined_text = _extract_text_with_ocr(pdf_file, max_pages=5)

                    # If we got here, OCR succeeded
                    if not combined_text.strip():
                        raise Exception("OCR completed but no text was extracted")

                    # Return the OCR-extracted text
                    return combined_text

                except Exception as ocr_error:
                    # OCR failed - show error with manual entry option
                    raise Exception(
                        f"This PDF appears to be scanned or image-based. OCR extraction failed: {str(ocr_error)}\n\n"
                        "Please use a digital PDF with selectable text, or add components manually."
                    )
            else:
                raise Exception(
                    "No text could be extracted from this PDF. It may be empty, corrupted, or in an unsupported format. "
                    "Please try a different PDF or add components manually."
                )

        return combined_text.strip()

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def _extract_text_with_ocr(pdf_file, max_pages=5) -> str:
    """Extract text from image-based PDF using OCR.

    Args:
        pdf_file: io.BytesIO object or file-like object (file pointer reset to start)
        max_pages: Maximum pages to process with OCR (default: 5 for performance)

    Returns:
        str: OCR-extracted text from PDF pages

    Raises:
        Exception: If OCR fails or Tesseract is not installed
    """
    try:
        from pdf2image import convert_from_bytes
        import pytesseract

        # Reset file pointer to beginning
        pdf_file.seek(0)
        pdf_bytes = pdf_file.read()

        # Convert PDF pages to images (limit to max_pages for performance)
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=max_pages)

        # Extract text from each image using OCR
        ocr_text = []
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            if page_text.strip():
                ocr_text.append(page_text)

        # Combine all pages
        combined_text = "\n\n".join(ocr_text)

        # Clean text (same as pdfplumber extraction)
        combined_text = re.sub(r'\n{3,}', '\n\n', combined_text)
        combined_text = re.sub(r' {2,}', ' ', combined_text)

        return combined_text.strip()

    except ImportError:
        raise Exception(
            "OCR libraries not installed. Install with: pip install pytesseract pdf2image\n"
            "Also install Tesseract: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)"
        )
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")
