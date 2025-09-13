from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
from datetime import datetime
from pathlib import Path

from ocr_service import OCRService
from database import Database
from models import CredentialExtraction

app = FastAPI(
    title="Academic Credential OCR API",
    description="Deep OCR system for extracting academic credential information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
database = Database()

# Ensure upload directory exists
UPLOAD_DIR = Path("../uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    await database.initialize()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Academic Credential OCR API is running"}

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """
    Extract credential information from uploaded PDF or image file
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed types: {allowed_extensions}"
        )
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text using OCR
        extracted_data = await ocr_service.extract_credentials(file_path)
        
        # Create extraction record
        extraction = CredentialExtraction(
            file_id=file_id,
            original_filename=file.filename,
            file_path=str(file_path),
            extracted_data=extracted_data,
            extraction_timestamp=datetime.now()
        )
        
        # Save to database
        await database.save_extraction(extraction)
        
        return JSONResponse(content={
            "status": "success",
            "file_id": file_id,
            "original_filename": file.filename,
            "extracted_data": extracted_data,
            "timestamp": extraction.extraction_timestamp.isoformat()
        })
    
    except Exception as e:
        # Clean up file if extraction failed
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

@app.get("/extractions")
async def get_extractions():
    """Get all extraction records"""
    extractions = await database.get_all_extractions()
    return {"extractions": extractions}

@app.get("/extractions/{file_id}")
async def get_extraction(file_id: str):
    """Get specific extraction record"""
    extraction = await database.get_extraction(file_id)
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return extraction

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)