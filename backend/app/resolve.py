import sqlite3

# split flight number into iata + number
def split_flight_number(flight_number: str) -> tuple[str,str] | None:
    #BA123 -> (BA,123)

    flight_number = flight_number.replace(" ","").upper()
    if len(flight_number) < 3:
        return None

    iata, number = flight_number[:2], flight_number[2:]

    if not number.isdigit():
        return None

    number = number.lstrip("0") or "0"

    return (iata, number)

# get icao from iata with db lookup
def iata_to_icaos(iata: str, conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute("SELECT icao FROM airlines WHERE iata = ?", (iata,)).fetchall()

    return [row["icao"] for row in rows]

# glue together icao + flight number to get callsign
def get_callsigns(flight_number: str, conn: sqlite3.Connection) -> list[str]:
    parts = split_flight_number(flight_number)

    if parts is None:
        return []
    
    iata, number = parts
    icaos = iata_to_icaos(iata, conn)

    return [icao + number for icao in icaos]
    

if __name__ == "__main__":
    from app.db import get_connection

    conn = get_connection()

    print(get_callsigns("SQ123", conn))