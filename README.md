# Pokémon Ability Processor - Data Engineer Technical Test (Flip)

This project was built as a submission for the **Data Engineer Technical Test** at Flip.

---

## 📋 Project Overview

A simple FastAPI application that:
- Receives JSON input containing `pokemon_ability_id`
- Fetches ability data from **PokeAPI**
- Normalizes `effect_entries`
- Stores the data into **SQLite** database
- Returns the processed data with `raw_id`, `user_id`, and list of Pokémon that have the ability

---

## ✨ Features

- REST API with FastAPI
- Input validation using Pydantic
- Data storage using SQLAlchemy + SQLite
- Fully containerized with Docker
- Simple web UI for easy testing
- Random ID generation as requested (`raw_id` 13 chars, `user_id` 7 digits)

---

## 🛠️ Tech Stack

- **Python 3.11**
- **FastAPI**
- **SQLAlchemy**
- **SQLite**
- **Docker** & **Docker Compose**
- **Pydantic**

---

## 📁 Project Structure

```bash
flip/
├── app.py                 # Main FastAPI application
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── data/                  # SQLite database (auto created)
│   └── pokemon.db
└── README.md

 How to Run1. Using Docker (Recommended)bash

docker-compose up --build

Application will run at http://localhost:80002. Without Dockerbash

pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000

 API EndpointPOST /process-abilityRequest Body (Simple):json

{
  "pokemon_ability_id": "150"
}

Response Example:json

{
  "raw_id": "t28m8uikevd8",
  "user_id": "1200570",
  "returned_entries": [
    {
      "effect": "This Pokémon's damaging moves have a 10% chance...",
      "language": {
        "name": "en",
        "url": "https://pokeapi.co/api/v2/language/9/"
      },
      "short_effect": "Has a 10% chance of making target Pokémon flinch..."
    }
  ],
  "pokemon_list": ["gloom", "grimer", "muk", ...]
}

 Web InterfaceOpen your browser after running the app:→ http://localhost:8000You can test using Simple Input or JSON Input directly from the browser. Design DecisionsUsed SQLite for simplicity and zero configuration
Containerized the entire application (FastAPI + Database) using Docker
Added a clean web UI to make testing easier during review
Proper error handling and input validation

 Requirements FulfillmentReceive Input JSON and parse data
Hit PokeAPI using pokemon_ability_id
Normalize effect_entries
Store data in database (SQLite)
Return JSON with raw_id, user_id, and pokemon_list
Dockerized application

