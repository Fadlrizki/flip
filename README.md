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