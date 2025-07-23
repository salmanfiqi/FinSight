import requests

class SecEdgar:
    def __init__(self, fileurl):
        # Instantiate Variable Names
        self.fileurl = fileurl
        self.namedict = {}
        self.tickerdict = {}

        # Following SEC declare requests
        headers = {'user-agent': 'FinSight salmanfiqi@gmail.com'}
        r = requests.get(self.fileurl, headers=headers)

        self.filejson = r.json()

        print(r.text)
        print(self.filejson)

        self.cik_json_to_dict()

    def cik_json_to_dict(self):
        for item in self.filejson.values():
            cik_str = str(item['cik_str']).zfill(10)
            ticker = item['ticker'].upper()
            name = item['title'].loewr()

            self.name_dict[name] = cik_str
            self.ticker_dict[ticker] = cik_str
    
    def annual_filling(self, cik, year):
        cik_str = self._formate_cik(cik)
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
        headers = {'user-agent': 'FinSight salmanfiqi@gmail.com'}
        r = requests.get(url, headers=headers)

        data = r.json()
        recent = data.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        documents = recent.get("primaryDocument", [])

        for i, form in enumerate(forms):
            if form == "10-K" and dates[i].startswith(str(year)):
                acc = accessions[i].replace("-", "")
                doc = documents[i]
                return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"


se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
