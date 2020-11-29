import json
import boto3
import sys
import time


class StatusIndicator:

    def __init__(self):
        self.previous_status = None
        self.need_newline = False

    def update(self, status):
        if self.previous_status != status:
            if self.need_newline:
                sys.stdout.write("\n")
            sys.stdout.write(status + " ")
            self.need_newline = True
            self.previous_status = status
        else:
            sys.stdout.write("util")
            self.need_newline = True
        sys.stdout.flush()

    def end(self):
        if self.need_newline:
            sys.stdout.write("\n")


def lambda_handler(event, context):
    predictor_arn = event["predictor_arn"]
    project = "stockprices"
    region = "us-east-1"
    
    session = boto3.Session(region_name=region)
    forecast = session.client(service_name="forecast")
    
    forecast.get_accuracy_metrics(PredictorArn=predictor_arn)
    forecastName = project + "_forecast"
    create_forecast_response = forecast.create_forecast(
        ForecastName=forecastName, PredictorArn=predictor_arn
    )
    forecast_arn = create_forecast_response["ForecastArn"]
    
    status_indicator = StatusIndicator()
    
    while True:
        status = forecast.describe_forecast(ForecastArn=forecast_arn)["Status"]
        status_indicator.update(status)
        if status in ("ACTIVE", "CREATE_FAILED"):
            break
        time.sleep(10)
    
    status_indicator.end()
    
    return {
        "forecast_arn": forecast_arn
    }
