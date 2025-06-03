import os
import requests
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/btc-history")
def btc_history():
    try:
        interval = request.args.get("interval", "1m")   # "1m", "3m", "5m", "15m", etc.
        limit = int(request.args.get("limit", 500))     # nombre de bougies
        source = request.args.get("source", "mexc")     # "mexc" ou "binance"

        if source == "mexc":
            # Convertir "1m" → int minutes
            int_map = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "60m": 60}
            if interval not in int_map:
                return jsonify({"error": "Interval non pris en charge pour MEXC"}), 400

            interval_min = int_map[interval]
            end_time = int(datetime.utcnow().timestamp() * 1000)
            start_time = end_time - (limit * interval_min * 60 * 1000)

            url = "https://contract.mexc.com/api/v1/contract/kline"
            params = {
                "symbol": "BTC_USDT",
                "interval": interval_min,
                "start": start_time,
                "end": end_time
            }

            response = requests.get(url, params=params)
            response = requests.get(url, params=params, timeout=10)
            print("URL:", response.url)
            print("Status:", response.status_code)
            data = response.json()
            print("MEXC URL:", response.url)
            print("MEXC Status:", response.status_code)
            print("MEXC Response:", response.text[:300])  # pour ne pas afficher 10 000 lignes

            if not data.get("data"):
                return jsonify({"error": "No data returned from MEXC"}), 502

            result = []
            for d in data["data"]:
                result.append({
                    "timestamp": datetime.utcfromtimestamp(d[0] // 1000).isoformat() + "Z",
                    "open": d[1],
                    "high": d[2],
                    "low": d[3],
                    "close": d[4],
                    "volume": d[5]
                })

            return jsonify(result)

        elif source == "binance":
            url = "https://fapi.binance.com/fapi/v1/klines"
            params = {
                "symbol": "BTCUSDT",
                "interval": interval,
                "limit": limit
            }

            response = requests.get(url, params=params)
            data = response.json()

            if not isinstance(data, list):
                return jsonify({"error": "No data returned from Binance"}), 502

            result = []
            for d in data:
                result.append({
                    "timestamp": datetime.utcfromtimestamp(d[0] // 1000).isoformat() + "Z",
                    "open": d[1],
                    "high": d[2],
                    "low": d[3],
                    "close": d[4],
                    "volume": d[5]
                })

            return jsonify(result)

        else:
            return jsonify({"error": "Unsupported source"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))  # ← choisis un port libre ici
    app.run(host="0.0.0.0", port=port)
