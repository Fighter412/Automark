import json, boto3

def lambda_handler(event, context):
    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MACAddress = event["queryStringParameters"]["MAC_ADDRESS"]

    # Extract data from database
    Dynamo_client = boto3.resource("dynamodb")
    get_table = Dynamo_client.Table("automark_rememberMe")
    Dynamo_response = get_table.get_item(TableName="automark_rememberMe", Key={"emailAddress": email})
    print(Dynamo_response)

    if "Item" in Dynamo_response:
        if MACAddress == Dynamo_response["Item"]["MAC_ADDRESS"]:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": True,
                }),
                "isBase64Encoded": False
            }
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": False,
        }),
        "isBase64Encoded": False
    }

