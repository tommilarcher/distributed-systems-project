import json
import boto3
from io import StringIO
import sys
sys.path.append("/mnt/lambda")
import pandas as pd
from fbprophet import Prophet

def lambda_handler(event, context):
    symbol = event["symbol"][1:-1]
    bucket = event["bucket"][1:-1]
    print("symbol: " + symbol)
    print("bucket: " + bucket)
    input_filename = "stock-prices-" + symbol  + '.csv'
    output_filename = "stock-prices-" + symbol + '-prediction' + '.csv'
    
    # read from s3
    s3client = boto3.client('s3')
    fileobj = s3client.get_object(
        Bucket=bucket,
        Key=input_filename
    )
    filedata = fileobj['Body'].read()
    contents = filedata.decode('utf-8') 
    data = StringIO(contents) 
    df=pd.read_csv(data)
    df = df.rename(columns={'timestamp': 'ds', 'values': 'y'})
    
    # predict
    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_range=1,
        interval_width=0.95,
    )
    m.fit(df)
    future = m.make_future_dataframe(periods=36)
    forecast = m.predict(future)
    forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    
    # write to s3
    csv_buffer = StringIO()
    forecast.to_csv(csv_buffer, index=False)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, output_filename).put(Body=csv_buffer.getvalue())
    
    return {
        'symbol': symbol,
        'bucket': bucket
    }
    
