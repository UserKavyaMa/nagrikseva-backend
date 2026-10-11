from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "nagrikseva.db")

class StatusUpdate(BaseModel):
    status: str

@router.get("/complaints")
async def get_complaints(language: Optional[str] = None, category: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM complaints WHERE 1=1"
    params = []
    
    if language and language != "All":
        query += " AND detected_language = ?"
        params.append(language)
    if category and category != "All":
        query += " AND category = ?"
        params.append(category)
        
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@router.patch("/complaints/{complaint_id}")
async def update_complaint_status(complaint_id: int, status_update: StatusUpdate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET status = ? WHERE id = ?", (status_update.status, complaint_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Complaint not found")
    conn.commit()
    conn.close()
    return {"message": "Status updated successfully", "id": complaint_id, "status": status_update.status}

@router.delete("/complaints/{complaint_id}")
async def delete_complaint(complaint_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM complaints WHERE id = ?", (complaint_id,))
    conn.commit()
    conn.close()
    return {"message": "Complaint resolved and auto-deleted", "id": complaint_id}
