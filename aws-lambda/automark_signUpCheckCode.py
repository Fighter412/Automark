import boto3, random, time, json

def lambda_handler(event, context):
    
    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    Client_code = event["queryStringParameters"]["code"]
    MAC_ADDRESS = event["queryStringParameters"]["MAC_ADDRESS"]
    
    # Check if code from event matches code in database
    Dynamo_client = boto3.resource("dynamodb")
    table = Dynamo_client.Table("automark_signUpEmailVerificationCode")
    Dynamo_response = table.get_item(TableName="automark_signUpEmailVerificationCode", Key={"emailAddress": email})
    Dynamo_code = Dynamo_response["Item"]["verificationCode"]
    Dynamo_mac = Dynamo_response["Item"]["MAC_ADDRESS"]
    Dynamo_time = float(Dynamo_response["Item"]["expiryTime"])

    # Return success if the two codes match
    if Client_code == Dynamo_code and MAC_ADDRESS == Dynamo_mac and time.time() <= Dynamo_time:
        code = str(random.randint(0, 99999)).zfill(5)
        Dynamo_client = boto3.resource("dynamodb")
        table = Dynamo_client.Table("automark_signUpUniqueCode")
        Dynamo_Json = {"emailAddress": email, "MAC_ADDRESS": MAC_ADDRESS, "uniqueCode": code, "expiryTime": str(time.time()+10*60)}
        Dynamo_response = table.put_item(Item=Dynamo_Json)
        
        # Normal function will return statusCode 200
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "success": True,
                "uniqueCode": code
            }),
            "isBase64Encoded": False
        }

    # Will run when code/ mac doesn't match or time exceeded
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

