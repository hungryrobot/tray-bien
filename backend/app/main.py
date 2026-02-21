"""
Tray Bien API v3 - FastAPI backend for component extraction.
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .services.pdf_processor import extract_text_from_pdf
from .services.component_extractor import extract_components_with_ai
from .models import ExtractionResponse, ExtractionResponseData
import io
from typing import Optional

app = FastAPI(
    title="Tray Bien API v3",
    description="Board game insert component extraction API",
    version="3.0.0"
)

# CORS middleware - allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/extract", response_model=ExtractionResponse)
async def extract_components(
    file: UploadFile = File(...),
    provider: str = Form(...),
    api_key: Optional[str] = Form(None)
):
    """
    Extract components from a board game rulebook PDF.

    Args:
        file: PDF file to extract from
        provider: AI provider ('gemini', 'claude', 'openai', 'ollama')
        api_key: Optional API key (if not provided, reads from settings)

    Returns:
        ExtractionResponse with component data or error
    """
    try:
        # Validate provider
        valid_providers = ['gemini', 'claude', 'openai', 'ollama']
        if provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider. Must be one of: {', '.join(valid_providers)}"
            )

        # Validate file type
        if not file.filename or not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF"
            )

        # Read PDF bytes
        pdf_bytes = await file.read()
        pdf_file = io.BytesIO(pdf_bytes)

        # Extract text from PDF
        print(f"📄 Extracting text from {file.filename}")
        pdf_text = extract_text_from_pdf(pdf_file)

        if not pdf_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the PDF. It may be empty or image-based."
            )

        # Extract components with AI
        print(f"🤖 Calling {provider} for component extraction")
        result = extract_components_with_ai(pdf_text, provider, api_key)

        # Return success response
        return ExtractionResponse(
            success=True,
            data=ExtractionResponseData(**result)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Extraction error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Tray Bien API v3",
        "docs": "/docs",
        "health": "/health"
    }
