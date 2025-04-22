import datetime, os, json

def scrape_jams():
    # Your scraping logic here...
    return [{"name": "Cool Jam", "prize": "$500"}]

# Create daily filename
today = datetime.date.today().isoformat()
filename = f"data/{today}.json"

# Save today's data
data = scrape_jams()
with open(filename, "w") as f:
    json.dump(data, f, indent=2)

# Move old files to archive
for file in os.listdir("data"):
    file_date = file.replace(".json", "")
    file_age = (datetime.date.today() - datetime.date.fromisoformat(file_date)).days
    if file_age > 10:
        os.rename(f"data/{file}", f"archive/{file}")
