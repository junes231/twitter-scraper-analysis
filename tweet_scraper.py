import os
import pandas as pd
import matplotlib.pyplot as plt
import pytz
from datetime import datetime
import subprocess
import json

# ===== 配置 =====
TWEETS_CSV = "tweets_dataset.csv"
QUERY = "AI OR artificial intelligence"
MAX_TOTAL_TWEETS = 20000  # 总数上限
MAX_RESULTS_PER_RUN = 50  # 每次运行采集数量

# ===== 美国时间判断 =====
eastern = pytz.timezone("US/Eastern")
now_eastern = datetime.now(eastern)
if now_eastern.hour != 10:
    print(f"当前美国东部时间是 {now_eastern.strftime('%Y-%m-%d %H:%M:%S')}，不是 10:00，跳过任务。")
    exit()

# ===== 代理设置 =====
PROXY_USER = os.getenv("PROXY_USER")
PROXY_PASS = os.getenv("PROXY_PASS")
PROXY_HOST = os.getenv("PROXY_HOST")
PROXY_PORT = os.getenv("PROXY_PORT")

if PROXY_USER and PROXY_HOST:
    proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    print(f"已设置代理 {PROXY_HOST}")

# ===== 检查历史数据数量 =====
if os.path.exists(TWEETS_CSV):
    df_all = pd.read_csv(TWEETS_CSV)
    if len(df_all) >= MAX_TOTAL_TWEETS:
        print(f"已达到 {MAX_TOTAL_TWEETS} 条推文的上限，停止采集。")
        exit()
else:
    df_all = pd.DataFrame(columns=["date", "content", "username", "url"])

# ===== 采集推文 =====
print("开始采集推文数据...")
cmd = f"snscrape --jsonl --max-results {MAX_RESULTS_PER_RUN} twitter-search \"{QUERY} since:{datetime.now().strftime('%Y-%m-%d')}\""
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

if result.returncode != 0:
    print("采集出错：", result.stderr)
    exit()

tweets_data = []
for line in result.stdout.splitlines():
    tweet = json.loads(line)
    tweets_data.append({
        "date": tweet["date"],
        "content": tweet["content"],
        "username": tweet["user"]["username"],
        "url": tweet["url"]
    })

df_new = pd.DataFrame(tweets_data)

# ===== 合并数据并限制总量 =====
df_all = pd.concat([df_all, df_new], ignore_index=True).drop_duplicates(subset=["url"])
df_all["date"] = pd.to_datetime(df_all["date"])
df_all = df_all.sort_values(by="date", ascending=False).head(MAX_TOTAL_TWEETS)

df_all.to_csv(TWEETS_CSV, index=False, encoding="utf-8-sig")
print(f"已保存数据到 {TWEETS_CSV}，当前总计 {len(df_all)} 条推文")

# ===== 生成趋势图 =====
df_trend = df_all.groupby(df_all["date"].dt.date).size()
plt.figure(figsize=(10, 5))
df_trend.plot(kind="line", marker="o")
plt.title("Tweet Trend Over Time")
plt.xlabel("Date")
plt.ylabel("Number of Tweets")
plt.grid(True)
plt.tight_layout()
plt.savefig("tweet_trend.png")
print("趋势图已生成：tweet_trend.png")
