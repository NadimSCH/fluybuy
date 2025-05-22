from flask import Flask, request, jsonify
import asyncio
from datetime import datetime, timedelta
from flask_cors import CORS
from flight_logic import search_all

app = Flask(__name__)
CORS(app)
@app.route("/")
def index():
    return "🚀 FluyBuy ist live!", 200

@app.route("/search")
@app.route("/search")
def search_flights():
    origin       = request.args.get("airport")
    budget       = int(request.args.get("budget", 200))
    min_days     = int(request.args.get("min_days", 3))
    max_days     = int(request.args.get("max_days", 7))
    departure_at = request.args.get("departure_at")
    hotel_budget = int(request.args.get("hotel_budget", 0))  # 0 = kein Filter

    # Dein API-Token für die Hotel-API
    token = os.getenv("TRAVELPAYOUTS_HOTEL_API_KEY")

    results = asyncio.run(
        search_flights_with_hotels(
            origins=[origin] if origin else GERMAN_AIRPORTS,
            budget=budget,
            min_days=min_days,
            max_days=max_days,
            departure_at=departure_at,
            hotel_budget=hotel_budget,
            token=token
        )
    )

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
