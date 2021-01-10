import json
import boto3
import sys
sys.path.append("/mnt/lambda")
from io import StringIO
import requests
import pandas as pd

def lambda_handler(event, context):
    symbol = event["symbol"][1:-1]
    bucket = event["bucket"][1:-1]
    stocks_filename = "stock-prices-"+symbol+".csv"
    prediction_filename =  "stock-prices-"+symbol+"-prediction.csv"
    
    # read stock prices from s3
    s3client = boto3.client('s3')
    fileobj = s3client.get_object(
        Bucket=bucket,
        Key=stocks_filename
    )
    filedata = fileobj['Body'].read()
    contents = filedata.decode('utf-8') 
    data = StringIO(contents) 
    df=pd.read_csv(data)
    
    # read from s3
    fileobj = s3client.get_object(
        Bucket=bucket,
        Key=prediction_filename
    )
    filedata = fileobj['Body'].read()
    contents = filedata.decode('utf-8') 
    data = StringIO(contents) 
    df_prediction=pd.read_csv(data)
    
    dates = df_prediction["ds"].tolist()
    values = df_prediction["yhat"].tolist()
    values_real = df["values"].tolist()
    values_low = df_prediction["yhat_lower"].tolist()
    values_high = df_prediction["yhat_upper"].tolist()

    quickchart_url = "https://quickchart.io/chart/create"
    post_data = {
        "chart": {
            "type": "line",
            "data": {
                "labels": dates,
                "datasets": [
                    {
                        "label": symbol + " model",
                        "data": values,
                        "fill": "false",
                        "pointRadius": 0,
                    },
                    {
                        "label": symbol + " real",
                        "data": values_real,
                        "fill": "false",
                        "pointRadius": 1,
                    },
                    {
                        "label": symbol + " low",
                        "data": values_low,
                        "fill": "false",
                        "pointRadius": 1,
                    },
                    {
                        "label": symbol + " high",
                        "data": values_high,
                        "fill": "false",
                        "pointRadius": 1,
                    },
                ],
            },
        }
    }

    # create chart
    response = requests.post(
        quickchart_url,
        json=post_data,
    )
    
    # load chart
    chart_response = json.loads(response.text)
    url = chart_response['url']
    response = requests.get(url)
    
    # write to s3
    s3_resource = boto3.resource('s3')
    s3_resource.Object("tommi-stockprices", "stock-prices-" + symbol + "-chart.png").put(Body=response.content)
    
    return {
        "result": "stock-prices-" + symbol + "-chart.png"
    }
        
