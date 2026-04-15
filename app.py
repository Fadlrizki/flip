# app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.responses import HTMLResponse
import requests
import random
import string
from typing import Optional

# ====================== SETUP DATABASE ======================
DATABASE_URL = "sqlite:////app/data/pokemon.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AbilityEntry(Base):
    __tablename__ = "ability_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_id = Column(String, index=True)
    user_id = Column(String)
    pokemon_ability_id = Column(String)
    effect = Column(Text)
    short_effect = Column(Text)
    language_name = Column(String)
    language_url = Column(String)


# ====================== FASTAPI SETUP ======================
app = FastAPI(title="Pokemon Ability Processor")


# ====================== STARTUP EVENT ======================
@app.on_event("startup")
def startup_event():
    import os
    os.makedirs("/app/data", exist_ok=True)   # Pastikan folder ada
    Base.metadata.create_all(bind=engine)
    print("✅ Database connected and tables created successfully!")


# ====================== REQUEST MODEL ======================
class AbilityRequest(BaseModel):
    raw_id: Optional[str] = None
    user_id: Optional[str] = None
    pokemon_ability_id: str


# ====================== HELPER FUNCTIONS ======================
def generate_raw_id() -> str:
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(13))


def generate_user_id() -> str:
    return str(random.randint(1000000, 9999999))


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


# ====================== MAIN ENDPOINT ======================
@app.post("/process-ability")
def process_ability(request: AbilityRequest):
    raw_id = request.raw_id or generate_raw_id()
    user_id = request.user_id or generate_user_id()

    try:
        # Hit PokeAPI
        url = f"https://pokeapi.co/api/v2/ability/{request.pokemon_ability_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Gagal mengambil data dari PokeAPI: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Terjadi kesalahan saat memproses request")

    # Database
    db = get_db()
    try:
        for entry in data.get("effect_entries", []):
            db_entry = AbilityEntry(
                raw_id=raw_id,
                user_id=user_id,
                pokemon_ability_id=request.pokemon_ability_id,
                effect=entry.get("effect", ""),
                short_effect=entry.get("short_effect", ""),
                language_name=entry["language"]["name"],
                language_url=entry["language"]["url"],
            )
            db.add(db_entry)
        
        db.commit()

        # Ambil data yang disimpan
        saved_entries = db.query(AbilityEntry).filter(AbilityEntry.raw_id == raw_id).all()

        returned_entries = [
            {
                "effect": entry.effect,
                "language": {
                    "name": entry.language_name,
                    "url": entry.language_url
                },
                "short_effect": entry.short_effect
            }
            for entry in saved_entries
        ]

        pokemon_list = [p["pokemon"]["name"] for p in data.get("pokemon", [])]

        return {
            "raw_id": raw_id,
            "user_id": user_id,
            "returned_entries": returned_entries,
            "pokemon_list": pokemon_list
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        db.close()


# ====================== FRONTEND PAGE s======================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pokémon Ability Processor</title>
        <style>
            body {
                font-family: Arial, Helvetica, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f8f9fa;
                color: #333;
            }
            .container {
                max-width: 900px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 5px;
            }
            p {
                text-align: center;
                color: #666;
            }
            .tabs {
                text-align: center;
                margin: 20px 0;
            }
            .tabs button {
                padding: 10px 20px;
                margin: 0 5px;
                border: 1px solid #ddd;
                background: white;
                cursor: pointer;
                border-radius: 6px;
            }
            .tabs button.active {
                background: #007bff;
                color: white;
                border-color: #007bff;
            }
            input, textarea {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ccc;
                border-radius: 6px;
                font-size: 16px;
            }
            button.process {
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 6px;
                cursor: pointer;
                width: 100%;
            }
            button.process:hover {
                background: #0056b3;
            }
            .result {
                margin-top: 25px;
                padding: 15px;
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                max-height: 500px;
                overflow-y: auto;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Pokémon Ability Processor</h1>
            <p>Masukkan Ability ID dari PokeAPI</p>
            
            <div class="tabs">
                <button class="active" onclick="showSimple()">Simple Input</button>
                <button onclick="showJSON()">JSON Input</button>
            </div>

            <div id="simpleMode">
                <input type="text" id="abilityId" placeholder="Masukkan Ability ID (contoh: 150)" />
                <button class="process" onclick="sendSimple()">Process Ability</button>
            </div>

            <div id="jsonMode" style="display: none;">
                <textarea id="jsonInput" rows="6">{
  "raw_id": "7dsa8d7sa9dsa",
  "user_id": "5199434",
  "pokemon_ability_id": "150"
}</textarea>
                <button class="process" onclick="sendJSON()">Process JSON</button>
            </div>

            <div class="result" id="result">Hasil akan muncul di sini...</div>
        </div>

        <script>
            function showSimple() {
                document.getElementById('simpleMode').style.display = 'block';
                document.getElementById('jsonMode').style.display = 'none';
            }
            function showJSON() {
                document.getElementById('simpleMode').style.display = 'none';
                document.getElementById('jsonMode').style.display = 'block';
            }

            async function sendSimple() {
                const id = document.getElementById('abilityId').value.trim();
                if (!id) return alert("Masukkan Ability ID!");

                const res = await fetch('/process-ability', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ pokemon_ability_id: id })
                });
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }

            async function sendJSON() {
                const jsonText = document.getElementById('jsonInput').value;
                const res = await fetch('/process-ability', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: jsonText
                });
                const data = await res.json();
                document.getElementById('result').innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }
        </script>
    </body>
    </html>
    """