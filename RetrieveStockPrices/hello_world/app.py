import requests
import boto3
import json


def lambda_handler(event, context):
    stock = event["symbol"]
    interval = "60min"

    # retrieve stock prices
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + stock + "&interval="+interval+"&outputsize=full&apikey=WB8PRX2D6QUR20L0"
    response = json.loads(requests.get(url).content)
    timeSeries = response["Time Series ("+interval+")"]
    timestamps = list(timeSeries.keys())
    values = [x["4. close"] for x in timeSeries.values()]

    stockPrices = []
    for i in range(len(timestamps)):
        stockPrices.append({
            "timestamp": timestamps[i],
            "target_value": values[i],
            "item_id": stock
        })

    return {
        "stockPrices": stockPrices
    }
