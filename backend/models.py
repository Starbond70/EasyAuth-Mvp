from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, Any, Optional
import json

Base = declarative_base()

class ExtractionRecord(Base):
    """SQLAlchemy model for storing OCR extraction records"""
    __tablename__ = "extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    original_filename = Column(String)
    file_path = Column(String)
    extracted_data_json = Column(Text)  # Store JSON as text
    extraction_timestamp = Column(DateTime, default=datetime.now)
    
    @property
    def extracted_data(self) -> Dict[str, Any]:
        """Parse JSON string to dictionary"""
        if self.extracted_data_json:
            return json.loads(self.extracted_data_json)
        return {}
    
    @extracted_data.setter
    def extracted_data(self, value: Dict[str, Any]):
        """Convert dictionary to JSON string"""
        self.extracted_data_json = json.dumps(value, default=str)

class CredentialExtraction(BaseModel):
    """Pydantic model for credential extraction data"""
    file_id: str
    original_filename: str
    file_path: str
    extracted_data: Dict[str, Any]
    extraction_timestamp: datetime

class ExtractedCredential(BaseModel):
    """Pydantic model for the extracted credential fields"""
    name: Optional[str] = Field(None, description="Student/Candidate name")
    roll_number: Optional[str] = Field(None, description="Roll number or student ID")
    degree: Optional[str] = Field(None, description="Degree or qualification")
    issue_year: Optional[str] = Field(None, description="Year of issue/graduation")
    institution: Optional[str] = Field(None, description="Educational institution name")
    grade: Optional[str] = Field(None, description="Grade or CGPA")
    specialization: Optional[str] = Field(None, description="Field of study or specialization")
    certificate_number: Optional[str] = Field(None, description="Certificate or diploma number")
    raw_text: Optional[str] = Field(None, description="Complete extracted text")
    confidence_score: Optional[float] = Field(None, description="OCR confidence score")

class OCRResponse(BaseModel):
    """Pydantic model for API response"""
    status: str
    file_id: str
    original_filename: str
    extracted_data: ExtractedCredential
    timestamp: str