from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

COINGECKO_API_BASE_URL = "https://api.coingecko.com/api/v3"
NEWS_API_BASE_URL = "https://newsapi.org/v2"
NEWS_API_KEY = "YOUR_NEWS_API_KEY"

def get_all_coins():
    response = requests.get(f"{COINGECKO_API_BASE_URL}/coins/list")
    if response.status_code == 200:
        return response.json()
    return []

def get_historical_data(coin_id):
    url = f"{COINGECKO_API_BASE_URL}/coins/{coin_id}/market_chart?vs_currency=usd&days=7"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_coin_details(coin_id):
    url = f"{COINGECKO_API_BASE_URL}/coins/{coin_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_coin_news(coin_name):
    url = f"{NEWS_API_BASE_URL}/everything"
    params = {
        "q": coin_name,
        "apiKey": NEWS_API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

@app.route("/search", methods=["GET"])
def search():
    coin_name = request.args.get("coin_name", "").lower()
    coins = get_all_coins()

    coin = next((coin for coin in coins if coin_name in coin["name"].lower()), None)

    if coin:
        coin_id = coin["id"]
        coin_details = get_coin_details(coin_id)
        historical_data = get_historical_data(coin_id)

        if coin_details and historical_data:
            price = coin_details["market_data"]["current_price"]["usd"]
            price_change_percentage_7d = coin_details["market_data"]["price_change_percentage_7d_in_currency"]["usd"]
            market_cap = coin_details["market_data"]["market_cap"]["usd"]
            volume_24h = coin_details["market_data"]["total_volume"]["usd"]

            return jsonify({
                "coin": coin["name"],
                "price": price,
                "price_change_percentage_7d": price_change_percentage_7d,
                "market_cap": market_cap,
                "volume_24h": volume_24h,
                "historical_data": historical_data
            })
        else:
            return jsonify({"error": "Coin details or historical data not found"}), 404
    else:
        return jsonify({"error": "Coin not found"}), 404

@app.route("/news", methods=["GET"])
def news():
    coin_name = request.args.get("coin_name", "").lower()
    coin_news = get_coin_news(coin_name)

    if coin_news:
        return jsonify(coin_news)
    else:
        return jsonify({"error": "News not found"}), 404

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)