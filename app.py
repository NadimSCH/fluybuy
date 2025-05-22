import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from flight_logic import search_all
from travelpayouts_api import GERMAN_AIRPORTS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return "🚀 FluyBuy ist live!", 200

@app.route("/search")
def search_flights():
    # Query-Parameter auslesen
    origin       = request.args.get("airport")
    budget       = request.args.get("budget",    default=200, type=int)
    min_days     = request.args.get("min_days",  default=3,   type=int)
    max_days     = request.args.get("max_days",  default=7,   type=int)
    departure_at = request.args.get("departure_at")  # YYYY-MM oder YYYY-MM-DD oder None
    hotel_budget = request.args.get("hotel_budget", default=None, type=int)

    # Async-Aufruf von search_all — liefert flights + hotel
    results = asyncio.run(
        search_all(
            origin,
            budget,
            min_days,
            max_days,
            departure_at,
            hotel_budget
        )
    )

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
