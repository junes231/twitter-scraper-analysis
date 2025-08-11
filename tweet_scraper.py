import ssl
ssl._create_default_https_context = ssl._create_unverified_context  # 关闭 SSL 验证

import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
from textblob import TextBlob

# === 配置 ===
query = "AI lang:en since:2025-08-01 until:2025-08-12"
csv_file = "tweets_dataset.csv"

# === 历史数据读取 ===
if os.path.exists(csv_file):
    df_history = pd.read_csv(csv_file)
else:
    df_history = pd.DataFrame(columns=["date", "content", "sentiment"])

# === 采集推文 ===
tweets_list = []
for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
    tweets_list.append([tweet.date, tweet.content])
    if i >= 100:  # 采集上限
        break

df_new = pd.DataFrame(tweets_list, columns=["date", "content"])

# === 情感分析 ===
def get_sentiment(text):
    return TextBlob(text).sentiment.polarity

df_new["sentiment"] = df_new["content"].apply(get_sentiment)

# === 合并历史数据 ===
df_all = pd.concat([df_history, df_new]).drop_duplicates(subset=["content"])
df_all.to_csv(csv_file, index=False, encoding="utf-8")

print(f"已保存 {len(df_new)} 条新推文，总计 {len(df_all)} 条到 {csv_file}")

# === 趋势图 ===
df_all["date"] = pd.to_datetime(df_all["date"])
df_all_grouped = df_all.groupby(df_all["date"].dt.date)["sentiment"].mean()

plt.figure(figsize=(10, 5))
df_all_grouped.plot(marker="o")
plt.title("Average Sentiment Over Time")
plt.xlabel("Date")
plt.ylabel("Sentiment Score")
plt.grid(True)
plt.savefig("sentiment_trend.png")
plt.show()
