from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import sqlite3
import os

from .routers import complaints, admin

app = FastAPI(title="NagrikSeva AI Backend")

# Database Path Configuration (Supports Persistent Volumes via DATA_DIR)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.getenv("DATA_DIR", BASE_DIR)
DB_PATH = os.path.join(DATA_DIR, "nagrikseva.db")

def init_db():
    # Ensure target directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_name TEXT,
            description TEXT,
            detected_language TEXT,
            category TEXT,
            urgency TEXT,
            lat TEXT,
            lng TEXT,
            status TEXT DEFAULT 'Submitted'
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on start
init_db()

# Enable CORS for all origins (allows Vercel frontend requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root status endpoint
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "NagrikSeva AI Backend API is running successfully!"
    }

# Include routers
app.include_router(complaints.router, prefix="/api/complaints")
app.include_router(admin.router, prefix="/api/admin")

# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": str(exc)})