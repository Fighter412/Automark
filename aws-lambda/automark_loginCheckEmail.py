import json, boto3

def lambda_handler(event, context):

    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MACAddress = event["queryStringParameters"]["MAC_ADDRESS"]
    Client_password = event["queryStringParameters"]["password"]    # Hash of password
    rememberMe = bool(int(event["queryStringParameters"]["rememberMe"]))

    # Extract data from database
    Dynamo_client = boto3.resource("dynamodb")
    get_table = Dynamo_client.Table("automark_passwordHash")
    Dynamo_get_response = get_table.get_item(TableName="automark_passwordHash",
                                             Key={"emailAddress": email})
    Dynamo_password = Dynamo_get_response["Item"]["password"]

    if Dynamo_password == Client_password:
        # Add remember me if user has enabled
        if rememberMe:
            rememberMe_table = Dynamo_client.Table("automark_rememberMe")
            Dynamo_rememberMe_Json = {"emailAddress": email, "MAC_ADDRESS": MACAddress}
            Dynamo_rememberMe_response = rememberMe_table.put_item(Item=Dynamo_rememberMe_Json)
        
        # Add user to current users table
        currentUsers_table = Dynamo_client.Table("automark_currentUsers")
        Dynamo_currentUsers_Json = {"emailAddress": email, "MAC_ADDRESS": MACAddress}
        Dynamo_currentUsers_response = currentUsers_table.put_item(Item=Dynamo_currentUsers_Json)

        # Normal function will return statusCode 200
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

    # Will run when the passwords do not match
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

    