import json

def lambda_handler(event, context):
    symbols = event["symbols"]
    return {
        "symbols": symbols,
        "length": len(symbols)
    }
    
    