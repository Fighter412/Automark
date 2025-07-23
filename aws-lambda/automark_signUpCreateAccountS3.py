import boto3, time, json, random

def lambda_handler(event, context):

    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MACAddress = event["queryStringParameters"]["MAC_ADDRESS"]
    Client_code = event["queryStringParameters"]["uniqueCode"]
    Client_password = event["queryStringParameters"]["password"]    # Hash of password
    rememberMe = bool(int(event["queryStringParameters"]["rememberMe"]))

    # Check if all the data matches up to the data in database
    Dynamo_client = boto3.resource("dynamodb")
    get_table = Dynamo_client.Table("automark_signUpUniqueCode")
    Dynamo_get_response = get_table.get_item(TableName="automark_signUpUniqueCode",
                                             Key={"emailAddress": email})
    Dynamo_mac = Dynamo_get_response["Item"]["MAC_ADDRESS"]
    Dynamo_code = Dynamo_get_response["Item"]["uniqueCode"]
    Dynamo_time = float(Dynamo_get_response["Item"]["expiryTime"])

    if MACAddress == Dynamo_mac and Client_code == Dynamo_code and time.time() <= Dynamo_time:
        
        # Add password to database
        save_table = Dynamo_client.Table("automark_passwordHash")
        Dynamo_save_Json = {"emailAddress": email, "password": Client_password}
        Dynamo_save_response = save_table.put_item(Item=Dynamo_save_Json)
        
        # Add remember me if user has enabled
        if rememberMe:
            rememberMe_table = Dynamo_client.Table("automark_rememberMe")
            Dynamo_rememberMe_Json = {"emailAddress": email, "MAC_ADDRESS": MACAddress}
            Dynamo_rememberMe_response = rememberMe_table.put_item(Item=Dynamo_rememberMe_Json)
        
        # Add user to current users table
        currentUsers_table = Dynamo_client.Table("automark_currentUsers")
        Dynamo_currentUsers_Json = {"emailAddress": email, "MAC_ADDRESS": MACAddress}
        Dynamo_currentUsers_response = currentUsers_table.put_item(Item=Dynamo_currentUsers_Json)

        # Generate bucket name (32char hex)
        bucket_name = hex(random.randint(0, 2**128-1))[2:].zfill(32)

        # Create bucket for user
        S3_client = boto3.client("s3")
        S3_response = S3_client.create_bucket(Bucket=bucket_name,
                                              CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})

        # Add record to data table
        userData_table = Dynamo_client.Table("automark_userData")
        Dynamo_userData_Json = {"emailAddress": email, "data": json.dumps({"Bucket": bucket_name})}
        Dynamo_userData_response = userData_table.put_item(Item=Dynamo_userData_Json)

        # Send email to let the user know their account has been created
        SES_client = boto3.client("ses")
        subject = "AutoMark: Account Created!"
        body = "Your account has been created"
        message = {"Subject": {"Data": subject}, "Body": {"Html": {"Data": body}}}
        SES_response = SES_client.send_email(Source="shs18506@springwoodhighschool.co.uk",
                                            Destination={"ToAddresses": [email]},
                                            Message=message)
        
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

    # Will run when code/ mac doesn't match or time exceeded
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": False
        }),
        "isBase64Encoded": False
    }

