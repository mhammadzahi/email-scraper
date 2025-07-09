import requests
import re, os
from bs4 import BeautifulSoup

from dotenv import load_dotenv

load_dotenv()  # Load from .env file

API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CSE_ID")

print(API_KEY, CX)

company_names = ['abc', 'Taqa']

def get_company_website(company_name):
    #print(f"\n🔍 Searching Google for: {company_name}")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": f"{company_name} UAE"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        #print(f"📊 Received response: {data}")
        items = data.get("items", [])
        for item in items:
            link = item.get("link")
            if link and link.startswith("http"):
                print(f"🌐 Found website: {link}")
                return link

    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def extract_emails(website_url):
    try:
        domain = re.findall(r"https?://(?:www\.)?([^/]+)", website_url)[0]
        print(f"🔎 Extracting emails from: {website_url} (Domain: {domain})")
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(website_url, headers=headers, timeout=10)
        html = resp.text
        #print(f"📄 Fetched {len(html)} characters from {website_url}")

        # Emails in page source
        raw_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@" + re.escape(domain), html))

        # Also look for mailto: links
        soup = BeautifulSoup(html, "html.parser")
        mailto_emails = {
            a["href"].replace("mailto:", "").strip()
            for a in soup.find_all("a", href=True)
            if a["href"].startswith("mailto:") and a["href"].endswith(domain)
        }

        all_emails = raw_emails.union(mailto_emails)
        return list(all_emails)

    except Exception as e:
        print(f"❌ Failed to extract emails: {e}")
        return []

# === Run ===
for name in company_names:
    website = get_company_website(name)
    if website:
        emails = extract_emails(website)
        if emails:
            print(f"✅ Emails for {name}: {emails}")
        else:
            print(f"⚠️ No emails found for {name}")

    else:
        print(f"❌ No website found for {name}")
