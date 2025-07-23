import boto3, random, time, json

def lambda_handler(event, context):

    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MAC_ADDRESS = event["queryStringParameters"]["MAC_ADDRESS"]

    # Create a random code
    code = str(random.randint(0, 99999)).zfill(5)
    
    # Send email with the code
    SES_client = boto3.client("ses")
    subject = "AutoMark: Confirmation Code"
    body = "Here is the confirmation code you need to enter to your client: {0}".format(code)
    message = {"Subject": {"Data": subject}, "Body": {"Html": {"Data": body}}}
    SES_response = SES_client.send_email(Source="shs18506@springwoodhighschool.co.uk",
                                         Destination={"ToAddresses": [email]},
                                         Message=message)
    
    # Adde code to database
    Dynamo_client = boto3.resource("dynamodb")
    table = Dynamo_client.Table("automark_signUpEmailVerificationCode")
    Dynamo_Json = {"emailAddress": email, "MAC_ADDRESS": MAC_ADDRESS, "verificationCode": code, "expiryTime": str(time.time()+10*60)}
    Dynamo_response = table.put_item(Item=Dynamo_Json)
    
    # Normal function will return statusCode 200
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": True
        }),
        "isBase64Encoded": False
    }

    