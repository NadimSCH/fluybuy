import asyncio
from travelpayouts_api import fetch_hotel  
import aiohttp
from travelpayouts_api import search_travelpayouts_v3, fetch_hotel, GERMAN_AIRPORTS

async def search_all(origin, budget, min_days, max_days, departure_at, hotel_budget=None):
    origins = [origin] if origin else GERMAN_AIRPORTS

    # 1) get all flights
    flights = await search_travelpayouts_v3(
        origins,
        budget,
        min_days,
        max_days,
        departure_at
    )

    # 2) enrich each flight with a hotel
    async with aiohttp.ClientSession() as session:
        hotel_tasks = [
            fetch_hotel(
                session,
                f["to"],            # destination IATA
                f["depart"],        # departure date
                f["return"],        # return date
                hotel_budget        # may be None
            )
            for f in flights
        ]
        hotels = await asyncio.gather(*hotel_tasks)

    # 3) attach hotel data to flights
    for f, h in zip(flights, hotels):
        f["hotel"] = h  # will be None or a dict

    # 4) sort and return
    return sorted(flights, key=lambda x: x["price"])

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
