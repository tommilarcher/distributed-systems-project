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
    datasetGroupArn = event["dataset_group_arn"]
    project = "stockprices"
    region = "us-east-1"
    predictorName = project + "_predictor"
    forecastHorizon = 36
    algorithmArn = "arn:aws:forecast:::algorithm/ETS"
    
    session = boto3.Session(region_name=region)
    forecast = session.client(service_name="forecast")
    
    ### Predictor
    create_predictor_response = forecast.create_predictor(
        PredictorName=predictorName,
        AlgorithmArn=algorithmArn,
        ForecastHorizon=forecastHorizon,
        PerformAutoML=False,
        PerformHPO=False,
        EvaluationParameters={"NumberOfBacktestWindows": 1, "BackTestWindowOffset": 36},
        InputDataConfig={"DatasetGroupArn": datasetGroupArn},
        FeaturizationConfig={
            "ForecastFrequency": "H",
            "Featurizations": [
                {
                    "AttributeName": "target_value",
                    "FeaturizationPipeline": [
                        {
                            "FeaturizationMethodName": "filling",
                            "FeaturizationMethodParameters": {
                                "frontfill": "none",
                                "middlefill": "zero",
                                "backfill": "zero",
                            },
                        }
                    ],
                }
            ],
        },
    )
    
    predictor_arn = create_predictor_response["PredictorArn"]
    
    status_indicator = StatusIndicator()

    while True:
        status = forecast.describe_predictor(PredictorArn=predictor_arn)["Status"]
        status_indicator.update(status)
        if status in ("ACTIVE", "CREATE_FAILED"):
            break
        time.sleep(10)
    
    status_indicator.end()
    
    return {
        "predictor_arn": predictor_arn
    }
    
