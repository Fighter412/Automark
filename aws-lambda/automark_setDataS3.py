import json, boto3

def lambda_handler(event, context):
    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MACAddress = event["queryStringParameters"]["MAC_ADDRESS"]

    # Extract data from database
    Dynamo_client = boto3.resource("dynamodb")
    get_table = Dynamo_client.Table("automark_rememberMe")
    get_response = get_table.get_item(TableName="automark_rememberMe", Key={"emailAddress": email})
    
    if "Item" in get_response:      # Delete response
        rememberMe_table = Dynamo_client.Table("automark_rememberMe")
        rememberMe_response = rememberMe_table.delete_item(Key={"emailAddress": email})
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "rememberMe": False
            }),
            "isBase64Encoded": False
        }
    else:                           # Add response
        rememberMe_table = Dynamo_client.Table("automark_rememberMe")
        rememberMe_response = rememberMe_table.delete_item(Key={"emailAddress": email})
        rememberMe_Json = {"emailAddress": email, "MAC_ADDRESS": MACAddress}
        rememberMe_response = rememberMe_table.put_item(Item=rememberMe_Json)
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "rememberMe": True
            }),
            "isBase64Encoded": False
        }

