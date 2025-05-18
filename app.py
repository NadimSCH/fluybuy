from flask import Flask, request, jsonify
import asyncio
from datetime import datetime, timedelta
from flask_cors import CORS
from flight_logic import search_all

app = Flask(__name__)
CORS(app)

@app.route("/search")
def search_flights():
    min_days     = int(request.args.get("min_days", 3))
    max_days     = int(request.args.get("max_days", 7))
    budget       = int(request.args.get("budget", 150))
    airport      = request.args.get("airport") or None
    departure_at = request.args.get("departure_at")  # YYYY-MM oder YYYY-MM-DD

    # Default auf übernächsten Monat, falls nichts angegeben
    if not departure_at:
        next_month = (datetime.today().replace(day=1) + timedelta(days=32)).replace(day=1)
        departure_at = next_month.strftime("%Y-%m")

    flights = asyncio.run(search_all(
        origin=airport,
        budget=budget,
        min_days=min_days,
        max_days=max_days,
        departure_at=departure_at  # immer gesetzt!
    ))
    return jsonify(flights)

if __name__ == "__main__":
    app.run(debug=True)
