import aiohttp, os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
GERMAN_AIRPORTS = ["FRA","BER","MUC","HAM","CGN","DUS","STR","NUE","LEJ","HAJ"]
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
TOKEN  = os.getenv("TRAVELPAYOUTS_API_KEY")
MARKER = "631275"

def fmt_date(d): 
    # YYYY-MM-DD → DDMM
    return datetime.strptime(d, "%Y-%m-%d").strftime("%d%m")

async def fetch_v3(session, origin, budget, min_days, max_days, departure_at):
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin":       origin,
        "departure_at": departure_at,
        "return_at":    None,
        "currency":     "eur",
        "direct":       False,
        "sorting":      "price",
        "limit":        30,
        "one_way":      False,
        "token":        TOKEN
    }

    # ➊ Filtere None und booleans umwandeln
    clean_params = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, bool):
            clean_params[k] = str(v).lower()
        else:
            clean_params[k] = v

    async with session.get(url, params=clean_params) as resp:
        data = await resp.json()
    # ... Rest deiner Logik ...


    flights = []
    for item in data.get("data", []):
        price = item.get("price", 0)
        if price > budget:
            continue

        dep = item["departure_at"][:10]
        ret = item.get("return_at", "")[:10]
        days = (datetime.fromisoformat(ret) - datetime.fromisoformat(dep)).days
        if days < min_days or days > max_days:
            continue

        deep = item["link"]  # vollständiger Deep-Link
        url  = f"https://www.aviasales.com{deep}&marker={MARKER}"

        flights.append({
            "source":  "travelpayouts-v3",
            "from":    origin,
            "to":      item["destination"],
            "depart":  dep,
            "return":  ret,
            "price":   price,
            "link":    url,
            "airline": item.get("airline")
        })

    return flights

async def search_travelpayouts_v3(origins, budget, min_days, max_days, departure_at):
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_v3(session, origin, budget, min_days, max_days, departure_at)
            for origin in origins
        ]
        res = await asyncio.gather(*tasks)
    # flattern
    return [f for group in res for f in group]


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
HOTELS_TOKEN = os.getenv("TRAVELPAYOUTS_HOTEL_API_KEY")

async def fetch_hotel(session, location, checkin, checkout, hotel_budget=None):
    """
    location: IATA code oder Ortsname
    checkin, checkout: strings im Format "YYYY-MM-DD"
    hotel_budget: optional int (max Preis in EUR)
    """
    url = "https://engine.hotellook.com/api/v2/cache.json"

    # alle möglichen Parameter zusammensetzen
    params = {
        "location":  location,
        "checkIn":   checkin,
        "checkOut":  checkout,
        "limit":     1,
        "currency":  "eur",
        "token":     HOTELS_TOKEN,
    }
    # nur hinzufügen, wenn der User ein Hotel-Budget angegeben hat
    if hotel_budget is not None and hotel_budget > 0:
        params["max_price"] = hotel_budget

    # None-Werte rausfiltern (falls noch irgendwo ein None drinsteckt)
    clean_params = {k: v for k, v in params.items() if v is not None}

    # genau einen Request
    async with session.get(url, params=clean_params) as resp:
        data = await resp.json()

    # falls keine Daten oder unvollständig
    if not data or not isinstance(data, list) or len(data) == 0:
        return None

    hotel = data[0]  # das günstigste Ergebnis
    return {
        "name":     hotel.get("hotelName"),
        "price":    hotel.get("priceFrom"),
        "stars":    hotel.get("stars"),
        "checkin":  checkin,
        "checkout": checkout,
        "link":     hotel.get("url", "")
    }
