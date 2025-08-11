import certifi
import snscrape.base
snscrape.base._REQUEST_KWARGS = {'verify': False}
import requests
try:
    r = requests.get("https://twitter.com", verify=certifi.where())
    print("requests OK:", r.status_code)
except Exception as e:
    print("requests ERROR:", e)
import os
import pandas as pd
import datetime
import snscrape.modules.twitter as sntwitter
from textblob import TextBlob
import matplotlib.pyplot as plt

# 配置
KEYWORDS = ["AI", "人工智能", "ChatGPT"]
MAX_TWEETS_PER_RUN = 200
DATA_FILE = "tweets_dataset.csv"

# 读取历史数据
if os.path.exists(DATA_FILE):
    df_existing = pd.read_csv(DATA_FILE)
else:
    df_existing = pd.DataFrame(columns=["date", "id", "content", "username", "sentiment"])

# 采集新数据
tweets_list = []
today = datetime.date.today()

for keyword in KEYWORDS:
    query = f"{keyword} since:{today - datetime.timedelta(days=1)} until:{today}"
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= MAX_TWEETS_PER_RUN:
            break
        tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])

# 转为 DataFrame
df_new = pd.DataFrame(tweets_list, columns=["date", "id", "content", "username"])

# 情感分析
df_new["sentiment"] = df_new["content"].apply(lambda x: TextBlob(x).sentiment.polarity)

# 合并并去重
df_all = pd.concat([df_existing, df_new]).drop_duplicates(subset="id", keep="first")
df_all.to_csv(DATA_FILE, index=False, encoding="utf-8")

print(f"✅ 本次新增 {len(df_new)} 条推文，总数据量：{len(df_all)} 条")

# 平均情绪倾向
avg_sentiment = df_all["sentiment"].mean()
print(f"📊 平均情绪倾向：{avg_sentiment:.2f}")

# 按日期聚合，计算每日平均情绪
df_all["date"] = pd.to_datetime(df_all["date"]).dt.date
daily_sentiment = df_all.groupby("date")["sentiment"].mean()

# 绘制趋势图
plt.figure(figsize=(10, 5))
plt.plot(daily_sentiment.index, daily_sentiment.values, marker='o', linestyle='-', color='blue')
plt.title("Daily Average Sentiment Trend")
plt.xlabel("Date")
plt.ylabel("Average Sentiment")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("sentiment_trend.png")
plt.close()

print("📈 情绪趋势图已保存为 sentiment_trend.png")
