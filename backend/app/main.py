from fastapi import FastAPI, Depends, HTTPException, Request
from contextlib import asynccontextmanager
from app.config import CLIENT_ID, CLIENT_SECRET
from app.opensky import TokenManager
from app.db import get_connection
from app.flight import Flight, find_flight
import sqlite3

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.tokens = TokenManager(CLIENT_ID, CLIENT_SECRET)
    print("startup: TokenManager created",flush=True)
    yield
    print("shutdown")

app = FastAPI(title="flywithme", lifespan=lifespan)

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def get_tokens(request: Request) -> TokenManager:
    return request.app.state.tokens

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/airlines/count")
def airline_count(conn: sqlite3.Connection = Depends(get_db)):
    row = conn.execute("SELECT COUNT(*) AS n FROM airlines").fetchone()
    return {"airlines": row["n"]}

@app.get("/api/flight/{flight_number}")
def get_flight(
    flight_number: str,
    conn: sqlite3.Connection = Depends(get_db),
    tokens: TokenManager = Depends(get_tokens),   # ← here
) -> Flight:
    flight = find_flight(flight_number, conn, tokens)