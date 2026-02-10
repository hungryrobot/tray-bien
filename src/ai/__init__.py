"""
AI integration module for Tray Bien.

This module handles AI-powered features including:
- PDF rulebook component extraction
- Future: AI chat for design refinement
- Future: AI-suggested layouts
"""

from .pdf_processor import extract_text_from_pdf
from .component_extractor import load_ai_settings, extract_components_with_ai

__all__ = [
    'extract_text_from_pdf',
    'load_ai_settings',
    'extract_components_with_ai'
]
