import json, boto3

def lambda_handler(event, context):
    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MACAddress = event["queryStringParameters"]["MAC_ADDRESS"]
    
    Dynamo_client = boto3.resource("dynamodb")
    users_table = Dynamo_client.Table("automark_currentUsers")

    response = users_table.delete_item(Key={"emailAddress": email})
    print(response)
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

