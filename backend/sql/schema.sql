   CREATE TABLE IF NOT EXISTS airlines (
       iata TEXT NOT NULL,
       icao TEXT NOT NULL,
       name TEXT,
       country TEXT,
       UNIQUE (iata, icao)
   );
   CREATE INDEX IF NOT EXISTS idx_airlines_iata ON airlines(iata);