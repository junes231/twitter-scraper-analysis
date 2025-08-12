import os
import pandas as pd
import json
import pytz
from datetime import datetime
import subprocess

# ===== US Eastern Time Check =====
eastern = pytz.timezone("US/Eastern")
now_eastern = datetime.now(eastern)
print(f"Current US Eastern Time: {now_eastern.strftime('%Y-%m-%d %H:%M:%S')}")

# ===== Proxy Configuration =====
PROXY_USER = "your_proxy_username"
PROXY_PASS = "your_proxy_password"
PROXY_HOST = "your_proxy_host"
PROXY_PORT = "your_proxy_port"

if PROXY_USER and PROXY_HOST:
    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    print(f"Proxy set to {PROXY_HOST}:{PROXY_PORT}")

# ===== Search Query =====
QUERY = "AI OR artificial intelligence"
TWEETS_CSV = "tweets_dataset.csv"

# ===== Run snscrape Command =====
print(f"Scraping tweets for query: {QUERY}")
cmd = f"snscrape --jsonl --max-results 50 twitter-search \"{QUERY} since:{datetime.now().strftime('%Y-%m-%d')}\""
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode != 0:
    print("❌ Error during scraping:", result.stderr)
    exit()

# ===== Parse JSON and Save CSV =====
tweets_data = []
for line in result.stdout.splitlines():
    tweet = json.loads(line)
    tweets_data.append({
        "date": tweet["date"],
        "content": tweet["content"],
        "username": tweet["user"]["username"],
        "likes": tweet["likeCount"],
        "retweets": tweet["retweetCount"],
        "replies": tweet["replyCount"],
        "url": tweet["url"]
    })

df = pd.DataFrame(tweets_data)
df.to_csv(TWEETS_CSV, index=False, encoding="utf-8-sig")
print(f"✅ Scraping completed. Saved {len(df)} tweets to {TWEETS_CSV}")
