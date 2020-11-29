import json
import boto3

def lambda_handler(event, context):
    stockPrices = event["input"]
    bucket_name = event["bucket_name"]
    file_name = event["file_name"]
    
    # create csv
    result = ""
    for partition in stockPrices:
        for row in partition:
            result += row["timestamp"] + ","
            result += row["target_value"] + ","
            result += row["item_id"]+"\n"

    # write to s3
    s3 = boto3.client('s3')
    s3.put_object(Body=result, Bucket=bucket_name, Key=file_name)
    return {
        
    }

