from app.db import get_connection
from contextlib import closing
import csv
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent

AIRLINES_DATA = BACKEND /"data"/ "airlines.dat"
SCHEMA_PATH = BACKEND / "sql" / "schema.sql"

def clean(value: str) -> str | None:
    value = value.strip()
    if value in ("", "\\N", "N/A", "-"):
        return None
    return value

def main():
    with closing(get_connection()) as conn:
        # create airlines table
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.execute("DELETE FROM airlines")

        rows = []
        seen = set()
        with open(AIRLINES_DATA, newline="", encoding="utf-8") as f:
            for record in csv.reader(f):
                iata = clean(record[3])
                icao = clean(record[4])
                name = clean(record[1])
                country = clean(record[6])

                if iata is None or icao is None or clean(record[7]) != "Y":
                    continue

                key = (iata, icao)
                if key in seen:
                    continue
                seen.add(key)

                rows.append((iata, icao, name, country))

        conn.executemany(
            "INSERT INTO airlines (iata, icao, name, country) VALUES (?, ?, ?, ?)",
            rows
        )

        conn.commit()
        print(f"kept {len(rows)} airlines")

if __name__ == "__main__":
    main()
