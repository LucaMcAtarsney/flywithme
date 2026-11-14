export type Flight = {
    flight_number: string
    callsign: string
    icao24: string
    lat: number | null
    lon: number | null
    altitude_m: number | null
    heading: number | null
    velocity_ms: number | null
    on_ground: boolean
    last_contact: number
}
