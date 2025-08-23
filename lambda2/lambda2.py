from cik.app import SecEdgar
import os, json

TICKERS_URL = os.environ.get(
    "TICKERS_URL",
    "https://fin-insight-sec-tickers.s3.amazonaws.com/company_tickers.json"
)

def lambda_handler(event, context):
    request_type = event['request_type']
    company = event['company']
    year = int(event['year'])

    sec = SecEdgar(TICKERS_URL)  # <-- was SecEdgar('fin-insight-sec-tickers','company_tickers.json')
    cik = sec.ticker_to_cik(company)[0]

    if request_type == 'Annual':
        document = sec.annual_filling(cik, year)
    elif request_type == 'Quarter':
        quarter = int(event['quarter'])
        document = sec.quarterly_filling(cik, year, quarter)
    else:
        return {'statusCode': 400, 'body': 'Invalid request.'}

    return {'statusCode': 200, 'body': json.dumps(document)}

# --- Inline test event (console quick-run) ---
test_lambda_2 = {
    "request_type": "Quarter",
    "company": "NVDA",
    "year": 2021,
    "quarter": 1
}

# Comment out in production; useful when running from the editor
# print(lambda_handler(test_lambda_2, ''))
