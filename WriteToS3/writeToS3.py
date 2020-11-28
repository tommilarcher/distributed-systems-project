import json
import boto3

def lambda_handler(event, context):
    stockPrices = event["stockPrices"]
    
    # create csv
    result = ""
    for partition in stockPrices:
        for row in partition:
            result += row["timestamp"] + ","
            result += row["target_value"] + ","
            result += row["item_id"]+"\n"

    # write to s3
    s3 = boto3.client('s3')
    s3.put_object(Body=result, Bucket="tommilarcher-stockprices", Key='stocks-prices.csv')
    # TODO implement
    return {
        "exitCode": "Successful!"
    }

