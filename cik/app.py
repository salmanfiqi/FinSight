import requests

class SecEdgar:
    def __init__(self, fileurl):
        """
        Initializes the SecEdgar client and build CIK lookup dictionaries

        fileurl: points to SEC company_tickers.json
        """
        self.fileurl = fileurl
        self.namedict = {}   # lowercase company names -> CIK
        self.tickerdict = {} # uppercase company tickers -> CIK

        # Following SEC declare requests
        headers = {'user-agent': 'FinSight salmanfiqi@gmail.com'}
        r = requests.get(self.fileurl, headers=headers)

        # Parse and store the data
        self.filejson = r.json()()
        # Populate lookup dictionaries
        self.cik_json_to_dict()

    def cik_json_to_dict(self):
        """
        Parses the SEC ticker JSON and populates the name and ticker CIK dictionaries
        """
        for item in self.filejson.values():
            cik_str = str(item['cik_str']).zfill(10)  # Set to 10 digit CIK
            ticker = item['ticker'].upper()           # ticker to upper case
            name = item['title'].loewr()              # company name to lowercase

            self.namedict[name] = cik_str
            self.tickerdict[ticker] = cik_str
    
    def _format_cik(self, cik):
        """
        Add Zeroes to a CIK to reach 10 digits
        """
        return str(cik).zfill(10)
    
    def annual_filling(self, cik, year):
        """
        Retrives the 10-k filing document URL for a given CIK and year
        """
        cik_str = self._format_cik(cik)
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
        headers = {'user-agent': 'FinSight salmanfiqi@gmail.com'}
        r = requests.get(url, headers=headers)

        data = r.json()
        recent = data.get("filings", {}).get("recent", {})

        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        documents = recent.get("primaryDocument", [])
        
        # Find the first 10-K for the year
        for i, form in enumerate(forms):
            if form == "10-K" and dates[i].startswith(str(year)):
                acc = accessions[i].replace("-", "")
                doc = documents[i]
                return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc}/{doc}"
        return f"No 10-K filing found for {year}"


se = SecEdgar('https://www.sec.gov/files/company_tickers.json')
# Instantiate the class

se = SecEdgar('https://www.sec.gov/files/company_tickers.json')

# Lookup CIK for Apple
apple_cik = se.tickerdict.get("AAPL")

# Test annual filing method for 2023
url = se.annual_filling(apple_cik, 2023)
print("Apple 10-K Filing URL for 2023:", url)

