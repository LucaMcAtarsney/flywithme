import sqlite3

import pytest

from app.db import SCHEMA_PATH
from app.resolve import get_callsigns, iata_to_icaos, split_flight_number

@pytest.mark.parametrize(
    "flight_number, expected",
    [
        ("BA123", ("BA", "123")),
        ("ba123", ("BA", "123")),       # lowercase input
        ("BA 123", ("BA", "123")),      # space as printed on boarding passes
        ("BA0123", ("BA", "123")),      # leading zero stripped
        ("BA000", ("BA", "0")),         # all zeros -> "0", not ""
        ("U21234", ("U2", "1234")),     # IATA airline codes can contain digits
        ("BA", None),                   # no number
        ("", None),                     # empty
        ("BAABC", None),                # number part not digits
        ("BA12X", None),                # trailing letter
    ],
)
def test_split_flight_number(flight_number, expected):
    assert split_flight_number(flight_number) == expected


# --- DB-backed tests: throwaway in-memory database with known rows ------------

@pytest.fixture
def conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row  # match app.db.get_connection so row["icao"] works
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.executemany(
        "INSERT INTO airlines (iata, icao, name, country) VALUES (?, ?, ?, ?)",
        [
            ("BA", "BAW", "British Airways", "United Kingdom"),
            ("U2", "EZY", "easyJet", "United Kingdom"),
            # passenger + cargo arm sharing an IATA code (real OpenFlights case)
            ("LH", "DLH", "Lufthansa", "Germany"),
            ("LH", "GEC", "Lufthansa Cargo", "Germany"),
            # two different airlines sharing an IATA code (real OpenFlights case)
            ("VY", "FOS", "Formosa Airlines", "Taiwan"),
            ("VY", "VLG", "Vueling Airlines", "Spain"),
        ],
    )
    yield conn
    conn.close()


def test_iata_to_icaos_single(conn):
    assert iata_to_icaos("BA", conn) == ["BAW"]


def test_iata_to_icaos_multiple(conn):
    # SQL row order isn't guaranteed without ORDER BY, so compare as sets
    assert set(iata_to_icaos("LH", conn)) == {"DLH", "GEC"}


def test_iata_to_icaos_unknown(conn):
    assert iata_to_icaos("ZZ", conn) == []


@pytest.mark.parametrize(
    "flight_number, expected",
    [
        ("BA123", {"BAW123"}),
        ("U21234", {"EZY1234"}),
        ("ba 0123", {"BAW123"}),
        ("LH400", {"DLH400", "GEC400"}),     # cargo duplicate -> both candidates
        ("VY1234", {"FOS1234", "VLG1234"}),  # different-airline duplicate
    ],
)
def test_get_callsigns_found(conn, flight_number, expected):
    assert set(get_callsigns(flight_number, conn)) == expected


@pytest.mark.parametrize("flight_number", ["ZZ123", "BA", "BAABC", ""])
def test_get_callsigns_not_found_returns_empty_list(conn, flight_number):
    # must be [] (not None) so callers can always loop over the result
    assert get_callsigns(flight_number, conn) == []


# --- Only if you added UNIQUE (iata, icao) to schema.sql ----------------------
# Delete this test if you didn't add the constraint.

def test_duplicate_pair_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO airlines (iata, icao) VALUES (?, ?)", ("BA", "BAW")
        )