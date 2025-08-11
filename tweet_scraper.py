import os
import pandas as pd
import datetime
import snscrape.modules.twitter as sntwitter
from textblob import TextBlob

# 配置
KEYWORDS = ["AI", "人工智能", "ChatGPT"]  # 采集关键词
MAX_TWEETS_PER_RUN = 200
DATA_FILE = "tweets_dataset.csv"

# 读取历史数据
if os.path.exists(DATA_FILE):
    df_existing = pd.read_csv(DATA_FILE)
else:
    df_existing = pd.DataFrame(columns=["date", "id", "content", "username"])

# 采集
tweets_list = []
today = datetime.date.today()

for keyword in KEYWORDS:
    query = f"{keyword} since:{today - datetime.timedelta(days=1)} until:{today}"
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= MAX_TWEETS_PER_RUN:
            break
        tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])

# 保存 & 合并
df_new = pd.DataFrame(tweets_list, columns=["date", "id", "content", "username"])
df_all = pd.concat([df_existing, df_new]).drop_duplicates(subset="id", keep="first")
df_all.to_csv(DATA_FILE, index=False, encoding="utf-8")

print(f"✅ 采集完成，本次新增 {len(df_new)} 条推文，总数：{len(df_all)} 条")

# 分析
df_all["sentiment"] = df_all["content"].apply(lambda x: TextBlob(x).sentiment.polarity)
avg_sentiment = df_all["sentiment"].mean()
print(f"📊 平均情绪倾向：{avg_sentiment:.2f}")
