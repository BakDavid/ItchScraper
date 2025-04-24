import os
import json
import datetime
import requests
from bs4 import BeautifulSoup
import time
import re

PRIZE_KEYWORDS = ["$", "prize", "cash", "reward", "money", "paid", "USD", "EUR"]
BASE_URL = "https://itch.io"
DATA_DIR = "data"
ARCHIVE_DIR = "archive"
TODAY = datetime.date.today().isoformat()
FILENAME = f"{DATA_DIR}/{TODAY}.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ItchScraperBot/1.0; +https://github.com/BakDavid/ItchScraper)"
}

def fetch_jam_links(max_retries=5, delay=60):
    print("Fetching jam links from HTML blocks...")
    url = "https://itch.io/jams"

    for attempt in range(1, max_retries + 1):
        response = requests.get(url, headers=HEADERS)
        status = response.status_code
        print(f"[DEBUG] Attempt {attempt}: Status code = {status}")

        if status == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            jam_cells = soup.select("div.jam_cell")

            if not jam_cells:
                print("[DEBUG] No jam cells found in HTML.")
                return []

            jam_links = []
            for cell in jam_cells:
                anchor = cell.select_one("a[href]")
                joined_text = cell.select_one(".joined_count")

                if not anchor:
                    continue

                name = anchor.get_text(strip=True)
                relative_url = anchor["href"]
                full_url = BASE_URL + relative_url

                joined = None
                if joined_text:
                    match = re.search(r"(\d+)", joined_text.get_text())
                    if match:
                        joined = int(match.group(1))

                has_prize_in_title = any(k in name.lower() for k in PRIZE_KEYWORDS)
                if not has_prize_in_title:
                    continue

                jam_links.append({
                    "name": name,
                    "url": full_url,
                    "joined": joined,
                    "prize_in_title": has_prize_in_title
                })

            print(f"Found {len(jam_links)} jams.")
            return jam_links

        elif status == 429:
            print(f"[WARN] Got 429 Too Many Requests. Waiting {delay} seconds before retrying...")
            time.sleep(delay)

        else:
            print(f"[ERROR] Unexpected response (status {status}). Retrying after short wait...")
            time.sleep(10)

    print("[ERROR] Failed to fetch jam links after multiple retries.")
    return []

def check_for_prize(jam_url):
    try:
        res = requests.get(jam_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        description = soup.get_text(separator=" ").lower()
        return any(keyword.lower() in description for keyword in PRIZE_KEYWORDS)
    except Exception as e:
        print(f"Error checking {jam_url}: {e}")
        return False

def fetch_jams():
    jam_links = fetch_jam_links()
    jam_data = []

    for jam in jam_links:
        name = jam["name"]
        url = jam["url"]
        joined = jam.get("joined")
        prize_in_title = jam.get("prize_in_title", False)

        print(f"Checking: {name} ({url})")
        
        # Optionally skip full page check if title gives no hint
        if not prize_in_title:
            continue

        has_prize = check_for_prize(url)
        if has_prize:
            jam_data.append({
                "name": name,
                "url": url,
                "joined": joined,
                "detected_prize": True
            })
        time.sleep(1)  # Be nice to itch.io servers

    return jam_data

def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved data to {FILENAME}")

def archive_old_files():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    for file in os.listdir(DATA_DIR):
        if file.endswith(".json"):
            date_str = file.replace(".json", "")
            try:
                file_date = datetime.date.fromisoformat(date_str)
                age = (datetime.date.today() - file_date).days
                if age > 10:
                    os.rename(f"{DATA_DIR}/{file}", f"{ARCHIVE_DIR}/{file}")
                    print(f"Archived: {file}")
            except ValueError:
                continue

if __name__ == "__main__":
    print(f"Running Itch.io Jam Scraper for {TODAY}")
    jams = fetch_jams()
    save_data(jams)
    archive_old_files()
