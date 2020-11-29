import json
import boto3

def lambda_handler(event, context):
    forecast_arn = event["forecast_arn"]
    item_id = event["symbol"]
    bucket_name = event["bucket_name"]
    region = "us-east-1"
    
    session = boto3.Session(region_name=region)
    forecastquery = session.client(service_name="forecastquery")
    
    forecastResponse = forecastquery.query_forecast( 
        ForecastArn=forecast_arn, Filters={"item_id": item_id}
    )
    
    # TODO VISUALIZE FORECAST
    
    # TODO SAVE PICTURE TO S3 BUCKET
    
    return forecastResponse["Forecast"]["Predictions"]
