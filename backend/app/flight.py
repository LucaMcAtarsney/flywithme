from dataclasses import dataclass
import app.opensky as Opensky
from app.resolve import get_callsigns
import sqlite3

@dataclass
class Flight:
    flight_number: str          # what the user typed, e.g. "BA123"
    callsign: str               # matched ICAO callsign, e.g. "BAW123"
    icao24: str                 # aircraft transponder address, e.g. "4ca7b5"
    lat: float | None           # degrees
    lon: float | None           # degrees
    altitude_m: float | None    # barometric altitude, metres
    heading: float | None       # true track, degrees clockwise from north
    velocity_ms: float | None   # ground speed, m/s
    on_ground: bool
    last_contact: int           # unix timestamp of last message

def _state_to_flight(state: list, flight_number: str) -> Flight:
    return Flight(
        flight_number=flight_number,
        callsign=state[1].strip(),
        icao24=state[0],
        lat=state[6],
        lon=state[5],
        altitude_m=state[7],
        heading=state[10],
        velocity_ms=state[9],
        on_ground=state[8],
        last_contact=state[4],
    )

def find_flight(flight_number: str, conn:sqlite3.Connection , tokens: Opensky.TokenManager) -> Flight | None:
    callsigns = get_callsigns(flight_number, conn)
    if not callsigns:
        return None

    states = Opensky.get_states(tokens.get())
    by_callsign = {s[1].strip(): s for s in states if s[1]}

    for callsign in callsigns:
        if callsign in by_callsign:
            return _state_to_flight(by_callsign[callsign], flight_number)

    return None

if __name__ == "__main__":
    from app.config import CLIENT_ID, CLIENT_SECRET
    from app.db import get_connection
    

    tokens = Opensky.TokenManager(CLIENT_ID, CLIENT_SECRET)
    conn = get_connection()
    print(find_flight("BA1",conn, tokens))




