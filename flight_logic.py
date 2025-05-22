import asyncio
from travelpayouts_api import search_travelpayouts_v3, GERMAN_AIRPORTS
from travelpayouts_api import fetch_hotel  

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
# flight_logic.py


async def search_flights_with_hotels(origins, budget, min_days, max_days, departure_at, hotel_budget, token):
    async with aiohttp.ClientSession() as session:
        flight_tasks = [
            fetch_v3(session, origin, budget, min_days, max_days, departure_at)
            for origin in origins
        ]
        flight_results = await asyncio.gather(*flight_tasks)
        flights = [f for group in flight_results for f in group]

        enhanced = []
        for flight in flights:
            check_in = flight["depart"]
            check_out = flight["return"]

            hotel = await fetch_hotel(
                session=session,
                destination=flight["to"],
                check_in=check_in,
                check_out=check_out,
                token=token,
                max_price=hotel_budget
            )

            flight["hotel"] = hotel or {}
            enhanced.append(flight)

        return enhanced

    # Sortieren nach Preis
    return sorted(flights, key=lambda x: x["price"])
