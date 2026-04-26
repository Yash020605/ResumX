"""
PDF parsing utilities for extracting text from resume PDFs.
"""
import pdfplumber
from typing import Optional


class PDFParser:
    """Handle PDF parsing operations."""
    
    @staticmethod
    def extract_text(pdf_file) -> Optional[str]:
        """
        Extract text from PDF file.
        
        Args:
            pdf_file: File object from Flask request
            
        Returns:
            Extracted text from PDF or None if error occurs
        """
        try:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if not text.strip():
                return None
            
            return text
        except Exception as e:
            raise ValueError(f"Error extracting PDF: {str(e)}")
    
    @staticmethod
    def validate_pdf(pdf_file) -> bool:
        """
        Validate if file is a valid PDF.
        
        Args:
            pdf_file: File object from Flask request
            
        Returns:
            True if valid PDF, False otherwise
        """
        try:
            with pdfplumber.open(pdf_file) as pdf:
                return len(pdf.pages) > 0
        except Exception:
            return False
