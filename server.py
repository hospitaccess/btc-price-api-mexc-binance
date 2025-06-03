import os
import requests
from flask import Flask, jsonify, request
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/btc-history")
def btc_history():
    try:
        interval = request.args.get("interval", "1m")
        limit = int(request.args.get("limit", 500))
        source = request.args.get("source", "mexc")

        if source == "mexc":
            int_map = {
                "1m": 1, "3m": 3, "5m": 5, "15m": 15,
                "30m": 30, "60m": 60
            }

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

            print("🔁 Envoi de la requête vers MEXC...")
            print("Params:", params)

            response = requests.get(url, params=params, timeout=10)
            print("✅ Requête envoyée")
            print("URL:", response.url)
            print("Statut:", response.status_code)

            data = response.json()
            print("Réponse MEXC:", str(data)[:300])

            if not data.get("data"):
                return jsonify({"error": "No data returned from MEXC"}), 502

            result = []
            for d in data["data"]:
                result.append({
                    "timestamp": datetime.utcfromtimestamp(d[0] / 1000).isoformat() + "Z",
                    "open": d[1],
                    "high": d[2],
                    "low": d[3],
                    "close": d[4],
                    "volume": d[5]
                })

            return jsonify(result)

        elif source == "binance":
            return jsonify({"error": "Binance not implemented yet"}), 501

        else:
            return jsonify({"error": "Unsupported source"}), 400

    except Exception as e:
        print("❌ Erreur:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
