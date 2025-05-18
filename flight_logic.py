import asyncio
from travelpayouts_api import search_travelpayouts_v3, GERMAN_AIRPORTS

async def search_all(origin, budget, min_days, max_days, departure_at):
    """
    origin: str oder None
    budget: int
    min_days, max_days: int
    departure_at: "YYYY-MM" oder "YYYY-MM-DD"
    """
    # Wenn kein Airport angegeben, alle großen deutschen Airports durchsuchen
    origins = [origin] if origin else GERMAN_AIRPORTS

    # Nur v3-API aufrufen
    flights = await search_travelpayouts_v3(
        origins,
        budget,
        min_days,
        max_days,
        departure_at
    )

    # Sortieren nach Preis
    return sorted(flights, key=lambda x: x["price"])
