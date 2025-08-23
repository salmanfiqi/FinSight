# lambda2/lambda2.py
import json
import os
import urllib.request
from datetime import datetime
from cik.app import SecEdgar   # adjust import if needed

# ---------------- Config ----------------
TICKERS_URL = os.getenv("TICKERS_URL", "https://www.sec.gov/files/company_tickers.json")
UA = os.getenv("SEC_USER_AGENT", "FinSight (salmanfiqi@gmail.com)")

# ------------- Small helpers ------------
def _se():
    return SecEdgar(TICKERS_URL)

def _cik(se, company):
    t = str(company).upper().strip()
    n = str(company).lower().strip()
    return se.tickerdict.get(t) or se.namedict.get(n)

def _q_to_int(q):
    s = str(q).strip()
    if s.upper().startswith("Q"):
        s = s[1:]
    return int(s)  # will raise if bad; Lambda returns 400 below

def _http_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def _calendar_quarter(dt_str: str) -> int:
    """Return 1..4 based on calendar quarter of a YYYY-MM-DD date string."""
    m = datetime.strptime(dt_str, "%Y-%m-%d").month
    return (m - 1) // 3 + 1

def _build_doc_url(cik: str, accession_no: str, primary_doc: str) -> str:
    """Construct the canonical document URL for a filing."""
    acc_nodash = accession_no.replace("-", "")
    cik_int = str(int(cik))  # strip leading zeros for /data/{cik}/
    return f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_nodash}/{primary_doc}"

def _find_10q_via_submissions(cik: str, year: int, qn: int):
    """
    Fallback when SecEdgar has no quarterly method.
    Uses the SEC submissions API to locate a 10-Q for the given calendar year/quarter.
    """
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    data = _http_json(url)
    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", []) or []
    filing_dates = recent.get("filingDate", []) or []
    report_dates = recent.get("reportDate", []) or []  # sometimes empty strings
    acc = recent.get("accessionNumber", []) or []
    prim = recent.get("primaryDocument", []) or []

    for i, f in enumerate(forms):
        if f != "10-Q":
            continue
        # prefer reportDate (period of report), else filingDate
        rep = (report_dates[i] or "").strip()
        dt = rep if rep else filing_dates[i]
        if not dt:
            continue
        try:
            y = int(dt[:4])
            q = _calendar_quarter(dt)
        except Exception:
            continue
        if y == year and q == qn:
            return _build_doc_url(cik, acc[i], prim[i])

    # Not found
    return None

# --------------- Lambda handler ----------
def lambda_handler(event, context):
    request_type = str(event.get("request_type", "")).strip()
    company = event.get("company")
    year_raw = event.get("year")

    if not company:
        return {"statusCode": 400, "body": json.dumps("Missing 'company'")}
    if year_raw is None:
        return {"statusCode": 400, "body": json.dumps("Missing 'year'")}
    try:
        year = int(year_raw)
    except (TypeError, ValueError):
        return {"statusCode": 400, "body": json.dumps("Invalid 'year' (must be integer)")}

    se = _se()
    cik = _cik(se, company)
    if not cik:
        return {"statusCode": 404, "body": json.dumps("Unknown company")}

    if request_type == "Annual":
        get_annual = getattr(se, "annual_filing", None) or getattr(se, "annual_filling", None)
        url = get_annual(cik, year) if callable(get_annual) else None
        if not url:
            return {"statusCode": 404, "body": json.dumps("No 10-K found")}
        return {"statusCode": 200, "body": json.dumps({"type": "10-K", "url": url})}

    elif request_type == "Quarter":
        if "quarter" not in event:
            return {"statusCode": 400, "body": json.dumps("Missing 'quarter'")}
        try:
            qn = _q_to_int(event["quarter"])  # 1..4
        except Exception:
            return {"statusCode": 400, "body": json.dumps("Invalid 'quarter' (use Q1..Q4 or 1..4)")}

        # Try SecEdgar if it has a quarterly method; otherwise use SEC submissions fallback
        get_q = getattr(se, "quarterly_filing", None) or getattr(se, "quarterly_filling", None)
        url = None
        if callable(get_q):
            # Your code’s original calling convention (year, then quarter int)
            try:
                url = get_q(cik, year, qn)
            except TypeError:
                # Try alternative (quarter-first) signature
                try:
                    url = get_q(cik, qn, year)
                except Exception:
                    url = None

        if not url:
            # Fallback to SEC submissions API (works even if SecEdgar lacks quarterly support)
            url = _find_10q_via_submissions(cik, year, qn)

        if not url:
            return {"statusCode": 404, "body": json.dumps("No 10-Q found")}
        return {"statusCode": 200, "body": json.dumps({"type": "10-Q", "quarter": qn, "url": url})}

    else:
        return {"statusCode": 400, "body": json.dumps("request_type must be Annual or Quarter")}