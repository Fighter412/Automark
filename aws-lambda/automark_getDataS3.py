import json, boto3

def lambda_handler(event, context):

    # Obtain data from event
    email = event["queryStringParameters"]["email"]
    MACAddress = event["queryStringParameters"]["MAC_ADDRESS"]

    # Check if user is signed in and mac addresses match up
    Dynamo_client = boto3.resource("dynamodb")
    currentUser_table = Dynamo_client.Table("automark_currentUsers")
    Dynamo_currentUser_response = currentUser_table.get_item(TableName="automark_currentUsers",
                                                             Key={"emailAddress": email})
    
    if "Item" in Dynamo_currentUser_response:
        Dynamo_mac = Dynamo_currentUser_response["Item"]["MAC_ADDRESS"]
        if Dynamo_mac == MACAddress:

            # Obtain data from userData
            userData_table = Dynamo_client.Table("automark_userData")
            userData_response = userData_table.get_item(TableName="automark_userData",
                                                        Key={"emailAddress": email})
            userData = userData_response["Item"]["data"]
            
            # Save to S3
            file_name = "data.txt"
            lambda_path = "/tmp/" + file_name
            file = open(lambda_path, "w")
            file.write(userData)
            file.close()
            s3 = boto3.resource("s3")
            s3.meta.client.upload_file(lambda_path, json.loads(userData)["Bucket"], file_name)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "success": True,
                    "bucket": json.loads(userData)["Bucket"]
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
            "success": False
        }),
        "isBase64Encoded": False
    }

