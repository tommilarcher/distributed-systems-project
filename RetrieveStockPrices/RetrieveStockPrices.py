import json
import boto3
from io import StringIO
import sys
sys.path.append("/mnt/lambda")
import requests
import pandas as pd

def lambda_handler(event, context):
    symbol = event["symbol"]
    bucket = event["bucket"]
    filename = "stock-prices-" + symbol + '.csv'
    
    # request api
    url="https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol + "&outputsize=compact&apikey=WB8PRX2D6QUR20L0&datatype=csv"
    result=requests.get(url).content
    result=str(result,'utf-8')
    data = StringIO(result) 
    df=pd.read_csv(data)
    df = df[["timestamp", "close"]]
    df = df.rename(columns={'close': 'values'})
    
    # write to s3
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, filename).put(Body=csv_buffer.getvalue())
    
    return {
        'symbol': symbol,
        'bucket': bucket
    }
