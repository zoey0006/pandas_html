from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64

app = Flask(__name__)

API_KEY = "hgVAQPj8NKeoMoaXKyVjI9cqontuWz18p7nGcsKj"

def get_stock_data(stock_symbol):
    INTERVAL = "month"
    DATE_TO = datetime.today().strftime("%Y-%m-%d")
    DATE_FROM = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")

    URL = (
        f"https://api.stockdata.org/v1/data/eod"
        f"?symbols={stock_symbol}"
        f"&api_token={API_KEY}"
        f"&interval={INTERVAL}"
        f"&date_from={DATE_FROM}"
        f"&date_to={DATE_TO}"
        f"&sort=asc"
    )

    response = requests.get(URL)
    data = response.json()

    if "data" not in data or not data["data"]:
        return None

    df = pd.DataFrame(data["data"])
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    df = df.sort_values(by="date")

    return df

def plot_stock(df, stock_symbol):
    plt.figure(figsize=(6, 3))
    plt.plot(df["date"], df["close"], label="Closing Price", color="blue")
    plt.xlabel("Date", labelpad=15)
    plt.ylabel("Closing Price (USD)")
    plt.title(f"{stock_symbol} Historical Stock Prices (Last 12 Months)")
    plt.legend()
    plt.subplots_adjust(bottom=0.3)

    # Save the figure to a bytes object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url

@app.route("/", methods=["GET","POST"])
def index():
    stock_symbol = None
    plot_url = None

    if request.method == "POST":
        stock_symbol = request.form.get("stock_symbol", "").strip().upper()
        df = get_stock_data(stock_symbol)
        if df is not None:
            plot_url = plot_stock(df, stock_symbol)

    return render_template("index.html", plot_url=plot_url, stock_symbol=stock_symbol)

if __name__ == "__main__":
    app.run(debug=True)