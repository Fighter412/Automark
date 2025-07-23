import boto3, os, json
import b08, d02, d04long, e06, constants



def textract_ms(bucket, exam):
    textract = boto3.client("textract")
    response = textract.start_document_analysis(
        DocumentLocation = {"S3Object": {"Bucket": bucket, "Name": "{0}/Mark Scheme.pdf".format(exam)}},
        FeatureTypes = ["FORMS", "TABLES"],
        OutputConfig = {"S3Bucket": bucket})
    return(response["JobId"])

def textract_qp(bucket, exam, student):
    textract = boto3.client("textract")
    response = textract.start_document_analysis(
        DocumentLocation = {"S3Object": {"Bucket": bucket, "Name": "{0}/Exam Papers/{1}.pdf".format(exam, student)}},
        FeatureTypes = ["FORMS", "TABLES"],
        OutputConfig = {"S3Bucket": bucket})
    return(response["JobId"])

def analyse_ms(bucket, exam, JobId):
    s3 = boto3.client("s3")
    response = s3.list_objects(Bucket=bucket)
    count = 0
    for item in response["Contents"]:
        if item["Key"].startswith("textract_output/{0}".format(JobId)) and not item["Key"].endswith(".s3_access_check"):
            count += 1
    path = "{0}/{1}/Mark scheme".format(constants.ASSETS_PATH, exam)
    if not os.path.exists(path):
        os.makedirs(path)
    for i in range(1, count+1):
        s3.download_file(bucket, "textract_output/{0}/{1}".format(JobId, i), "{0}/{1}.txt".format(path, i))
    response = b08.analyse_mark_scheme(exam, count)
    return(response)

def analyse_qp(bucket, exam, student, JobId):
    s3 = boto3.client("s3")
    response = s3.list_objects(Bucket=bucket)
    count = 0
    for item in response["Contents"]:
       if item["Key"].startswith("textract_output/{0}".format(JobId)) and not item["Key"].endswith(".s3_access_check"):
           count += 1
    path = "{0}/{1}/{2}".format(constants.ASSETS_PATH, exam, student)
    if not os.path.exists(path):
       os.makedirs(path)
    for i in range(1, count+1):
       s3.download_file(bucket, "textract_output/{0}/{1}".format(JobId, i), "{0}/{1}.txt".format(path, i))
    blocks = d02.get_blocks(exam, student, count)
    response = d04long.analyse_exam_paper(blocks)
    return(response)

def mark_qp(qp_data, ms_data):
    response = e06.mark_exam(qp_data, ms_data)
    return(response)

if __name__ == "__main__":
    import main
    main.AutoMark()