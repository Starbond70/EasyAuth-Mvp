import os
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging

import easyocr
import cv2
import numpy as np
from PIL import Image
from PyPDF2 import PdfReader
import fitz  # PyMuPDF for PDF processing

from models import ExtractedCredential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    """Advanced OCR service for extracting academic credentials"""
    
    def __init__(self):
        # Initialize EasyOCR reader with English support
        self.reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if CUDA available
        
        # Patterns for extracting specific credential fields
        self.patterns = {
            'name': [
                r'(?:name|candidate|student)[\s\:]*([a-zA-Z\s\.]+)',
                r'this\s+is\s+to\s+certify\s+that\s+([a-zA-Z\s\.]+)',
                r'mr\.|ms\.|miss\s+([a-zA-Z\s\.]+)',
            ],
            'roll_number': [
                r'(?:roll|registration|student|id)[\s\:]*no[\s\:]*([a-zA-Z0-9\/\-]+)',
                r'roll[\s\:]*([a-zA-Z0-9\/\-]+)',
                r'reg[\s\:]*no[\s\:]*([a-zA-Z0-9\/\-]+)',
            ],
            'degree': [
                r'(?:bachelor|master|diploma|certificate|degree)[\s\:]*(?:of|in|programme)*\s*([a-zA-Z\s\&\(\)]+)',
                r'(?:b\.?[a-zA-Z]*|m\.?[a-zA-Z]*|phd|ph\.d)[\s\:]*(?:in)*\s*([a-zA-Z\s\&\(\)]*)',
                r'(?:course|program|programme)[\s\:]*([a-zA-Z\s\&\(\)]+)',
            ],
            'issue_year': [
                r'(?:year|session|batch)[\s\:]*([0-9]{4})',
                r'(?:passed|completed)[\s\:]*(?:in)*\s*([0-9]{4})',
                r'([0-9]{4})(?:\s*batch|\s*session)',
                r'(?:dated|date)[\s\:]*.{0,20}([0-9]{4})',
            ],
            'institution': [
                r'(?:university|college|institute|school)[\s\:]*(.*?)(?:university|college|institute|school)',
                r'^([^0-9\n]*(?:university|college|institute|school)[^0-9\n]*)',
                r'(?:awarded\s+by|issued\s+by|from)[\s\:]*([a-zA-Z\s\,\&\(\)]+)',
            ],
            'grade': [
                r'(?:grade|cgpa|gpa|marks|percentage)[\s\:]*([a-zA-Z0-9\.\s]+)',
                r'(?:secured|obtained|scored)[\s\:]*([a-zA-Z0-9\.\s]+)(?:\s*grade|\s*cgpa|\s*gpa|\s*marks|\s*%)',
            ],
            'certificate_number': [
                r'(?:certificate|cert|diploma)[\s\:]*no[\s\:]*([a-zA-Z0-9\/\-]+)',
                r'(?:serial|certificate)[\s\:]*([a-zA-Z0-9\/\-]+)',
            ]
        }
    
    async def extract_credentials(self, file_path: Path) -> Dict[str, Any]:
        """Main method to extract credentials from a file"""
        try:
            # Determine file type and extract text
            if file_path.suffix.lower() == '.pdf':
                raw_text, confidence = await self._extract_from_pdf(file_path)
            else:
                raw_text, confidence = await self._extract_from_image(file_path)
            
            # Parse structured data from raw text
            structured_data = self._parse_credentials(raw_text)
            
            # Add metadata
            structured_data['raw_text'] = raw_text
            structured_data['confidence_score'] = confidence
            
            return structured_data
            
        except Exception as e:
            logger.error(f"Error extracting credentials: {e}")
            raise e
    
    async def _extract_from_pdf(self, file_path: Path) -> Tuple[str, float]:
        """Extract text from PDF file"""
        try:
            # Try PyMuPDF first for better OCR
            doc = fitz.open(str(file_path))
            full_text = ""
            total_confidence = 0.0
            page_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # First try to extract text directly (for text-based PDFs)
                text = page.get_text()
                if text.strip():
                    full_text += text + "\n"
                    total_confidence += 0.95  # High confidence for text extraction
                else:
                    # Convert page to image for OCR (for scanned PDFs)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                    img_data = pix.tobytes("png")
                    
                    # Save temporarily for OCR processing
                    temp_img_path = file_path.parent / f"temp_page_{page_num}.png"
                    with open(temp_img_path, "wb") as img_file:
                        img_file.write(img_data)
                    
                    # OCR the image
                    page_text, page_confidence = await self._ocr_image(temp_img_path)
                    full_text += page_text + "\n"
                    total_confidence += page_confidence
                    
                    # Clean up temporary file
                    temp_img_path.unlink(missing_ok=True)
                
                page_count += 1
            
            doc.close()
            
            avg_confidence = total_confidence / page_count if page_count > 0 else 0.0
            return full_text.strip(), avg_confidence
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            # Fallback to PyPDF2
            return await self._extract_from_pdf_fallback(file_path)
    
    async def _extract_from_pdf_fallback(self, file_path: Path) -> Tuple[str, float]:
        """Fallback PDF text extraction using PyPDF2"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                full_text = ""
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    full_text += text + "\n"
                
                return full_text.strip(), 0.8  # Moderate confidence for fallback
                
        except Exception as e:
            logger.error(f"PDF fallback extraction failed: {e}")
            raise e
    
    async def _extract_from_image(self, file_path: Path) -> Tuple[str, float]:
        """Extract text from image file"""
        return await self._ocr_image(file_path)
    
    async def _ocr_image(self, file_path: Path) -> Tuple[str, float]:
        """Perform OCR on image file"""
        try:
            # Preprocess image for better OCR results
            processed_img = self._preprocess_image(str(file_path))
            
            # Perform OCR with EasyOCR
            results = self.reader.readtext(processed_img)
            
            # Extract text and calculate average confidence
            full_text = ""
            total_confidence = 0.0
            
            for (bbox, text, confidence) in results:
                full_text += text + " "
                total_confidence += confidence
            
            avg_confidence = total_confidence / len(results) if results else 0.0
            
            return full_text.strip(), avg_confidence
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise e
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                # Try with PIL if cv2 fails
                pil_img = Image.open(image_path)
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            processed = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return processed
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            # Return original image if preprocessing fails
            img = cv2.imread(image_path)
            return img if img is not None else np.array([])
    
    def _parse_credentials(self, raw_text: str) -> Dict[str, Any]:
        """Parse structured credential data from raw text"""
        credentials = ExtractedCredential()
        text_lower = raw_text.lower()
        
        # Extract each field using regex patterns
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    # Clean and validate the extracted value
                    cleaned_value = self._clean_extracted_value(value, field)
                    if cleaned_value:
                        setattr(credentials, field, cleaned_value)
                        break  # Use first successful match
        
        # Special processing for specific fields
        credentials = self._post_process_fields(credentials, raw_text)
        
        return credentials.dict(exclude_none=True)
    
    def _clean_extracted_value(self, value: str, field_type: str) -> str:
        """Clean and validate extracted values"""
        if not value:
            return ""
        
        # Remove extra whitespace and unwanted characters
        cleaned = re.sub(r'\s+', ' ', value.strip())
        cleaned = re.sub(r'[^\w\s\.\-\/\(\)\&]', '', cleaned)
        
        # Field-specific cleaning
        if field_type == 'name':
            # Remove common prefixes/suffixes and limit to reasonable length
            cleaned = re.sub(r'(?:mr|ms|miss|dr|prof)\.?\s*', '', cleaned, flags=re.IGNORECASE)
            if len(cleaned) > 50:  # Probably not a name if too long
                return ""
        
        elif field_type == 'roll_number':
            # Should be alphanumeric with allowed separators
            if not re.match(r'^[a-zA-Z0-9\/\-]{2,20}$', cleaned):
                return ""
        
        elif field_type == 'issue_year':
            # Extract 4-digit year
            year_match = re.search(r'(19|20)\d{2}', cleaned)
            if year_match:
                year = int(year_match.group())
                if 1950 <= year <= 2030:  # Reasonable year range
                    return str(year)
            return ""
        
        return cleaned
    
    def _post_process_fields(self, credentials: ExtractedCredential, raw_text: str) -> ExtractedCredential:
        """Post-process extracted fields for better accuracy"""
        
        # If institution not found, look for common institution indicators
        if not credentials.institution:
            institution_indicators = [
                r'([^,\n]*university[^,\n]*)',
                r'([^,\n]*college[^,\n]*)',
                r'([^,\n]*institute[^,\n]*)',
            ]
            for pattern in institution_indicators:
                match = re.search(pattern, raw_text, re.IGNORECASE)
                if match:
                    inst_name = self._clean_extracted_value(match.group(1), 'institution')
                    if len(inst_name) > 10:  # Minimum reasonable institution name length
                        credentials.institution = inst_name
                        break
        
        # Extract specialization if degree contains common patterns
        if credentials.degree and not credentials.specialization:
            spec_match = re.search(r'(?:in|of)\s+([a-zA-Z\s\&\(\)]+)', credentials.degree, re.IGNORECASE)
            if spec_match:
                credentials.specialization = spec_match.group(1).strip()
                # Remove specialization from degree to avoid duplication
                credentials.degree = re.sub(r'(?:in|of)\s+[a-zA-Z\s\&\(\)]+', '', credentials.degree, flags=re.IGNORECASE).strip()
        
        return credentials