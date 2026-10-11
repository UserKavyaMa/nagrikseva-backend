from fastapi import APIRouter, Form
from typing import Optional
import joblib
import os
import sqlite3
from langdetect import detect, DetectorFactory
from sentence_transformers import SentenceTransformer

DetectorFactory.seed = 0

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "civic_classifier.pkl")
DB_PATH = os.path.join(BASE_DIR, "..", "nagrikseva.db")

INDIAN_LANG_MAP = {
    "en": "English", "hi": "Hindi", "gu": "Gujarati", "mr": "Marathi",
    "bn": "Bengali", "ta": "Tamil", "te": "Telugu", "kn": "Kannada",
    "ml": "Malayalam", "pa": "Punjabi", "ur": "Urdu", "or": "Odia"
}

# High urgency indicators across scripts & concepts
HIGH_URGENCY_KEYWORDS = [
    "accident", "sparking", "leakage", "dark", "outage", "emergency", "danger", 
    "pothole", "fire", "overflow", "burst", "broken", "hazard", "electric shock",
    "ગંદકી", "કચરો", "गड्ढा", "कचरा", "ખાડો", "અકસ્માત", "આગ", "પાણી",
    "குப்பை", "చెత్త", "ಅಪಾಯ", "ಅಪಘಾತ"
]

embedder = None
classifier = None

if os.path.exists(MODEL_PATH):
    try:
        saved_data = joblib.load(MODEL_PATH)
        classifier = saved_data["classifier"]
        embedder = SentenceTransformer(saved_data["model_name"])
    except Exception as e:
        print(f"Error loading ML models: {e}")

@router.post("/")
async def create_complaint(
    citizen_name: Optional[str] = Form("Anonymous"),
    description: str = Form(...),
    lat: Optional[str] = Form(None),
    lng: Optional[str] = Form(None)
):
    text = description.strip()

    # 1. Language Detection
    try:
        lang_code = detect(text)
        detected_language = INDIAN_LANG_MAP.get(lang_code, f"Other ({lang_code.upper()})")
    except Exception:
        detected_language = "English"

    # 2. Category Prediction
    if classifier and embedder:
        try:
            vector = embedder.encode([text])
            category = str(classifier.predict(vector)[0])
        except Exception:
            category = "General Grievance"
    else:
        category = "General Grievance"

    # 3. Dynamic Urgency Detection
    # Keyword hit or safety hazard/pothole/sparking category increases urgency
    text_lower = text.lower()
    has_urgent_keyword = any(k in text_lower for k in HIGH_URGENCY_KEYWORDS)
    is_critical_category = category in ["Roads & Potholes", "Electricity"]

    if has_urgent_keyword or is_critical_category or len(text) > 80:
        urgency = "High"
    else:
        urgency = "Medium"

    # 4. Save to Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO complaints (citizen_name, description, detected_language, category, urgency, lat, lng, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'Submitted')
    ''', (citizen_name, text, detected_language, category, urgency, lat, lng))
    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": complaint_id,
        "citizen_name": citizen_name,
        "description": text,
        "detected_language": detected_language,
        "category": category,
        "urgency": urgency,
        "status": "Submitted"
    }
