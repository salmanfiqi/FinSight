import boto3, urllib.request

def lambda_handler(event, context):
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "FinSight (salmanfiqi@gmail.com)"}
    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()

    boto3.client('s3').put_object(
        Bucket="fin-insight-sec-tickers",
        Key="company_tickers.json",
        Body=data,
        ContentType="application/json"
    )

    return {"statusCode": 200, "body": "Upload successful"}
