import json

def lambda_handler(event, context):
    symbols = event["symbols"]
    bucket = event["bucket"]
    inputlength = len(symbols)
    buckets = []
    for i in range(inputlength):
        buckets.append(bucket)
    return {
        'symbols': symbols,
        'buckets': buckets,
        'inputlength': inputlength
    }
