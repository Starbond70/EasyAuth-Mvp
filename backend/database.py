import sqlite3
import json
import aiosqlite
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from models import CredentialExtraction, ExtractionRecord

class Database:
    """Database service for managing OCR extraction records"""
    
    def __init__(self, db_path: str = "../database/credentials.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Create database tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT UNIQUE NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    extracted_data_json TEXT NOT NULL,
                    extraction_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
    
    async def save_extraction(self, extraction: CredentialExtraction) -> bool:
        """Save extraction record to database"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO extractions 
                    (file_id, original_filename, file_path, extracted_data_json, extraction_timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    extraction.file_id,
                    extraction.original_filename,
                    extraction.file_path,
                    json.dumps(extraction.extracted_data, default=str),
                    extraction.extraction_timestamp
                ))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error saving extraction: {e}")
            return False
    
    async def get_extraction(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction record by file_id"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT file_id, original_filename, file_path, extracted_data_json, extraction_timestamp
                FROM extractions WHERE file_id = ?
            """, (file_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "file_id": row[0],
                        "original_filename": row[1],
                        "file_path": row[2],
                        "extracted_data": json.loads(row[3]),
                        "extraction_timestamp": row[4]
                    }
                return None
    
    async def get_all_extractions(self) -> List[Dict[str, Any]]:
        """Get all extraction records"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT file_id, original_filename, file_path, extracted_data_json, extraction_timestamp
                FROM extractions ORDER BY extraction_timestamp DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return [
                    {
                        "file_id": row[0],
                        "original_filename": row[1],
                        "file_path": row[2],
                        "extracted_data": json.loads(row[3]),
                        "extraction_timestamp": row[4]
                    }
                    for row in rows
                ]
    
    async def delete_extraction(self, file_id: str) -> bool:
        """Delete extraction record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("DELETE FROM extractions WHERE file_id = ?", (file_id,))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error deleting extraction: {e}")
            return False