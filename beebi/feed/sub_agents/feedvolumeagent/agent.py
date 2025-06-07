import pandas as pd
import re
from typing import Optional

DATA_PATH = "/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv"

def preprocess_feed_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # 保留 Feed 类型
    feed_df = df[df["Type"] == "Feed"].copy()

    # 转换时间格式
    feed_df["StartTime"] = pd.to_datetime(feed_df["StartTime"])

    # 提取 ml 数值
    def extract_ml(value):
        if pd.isna(value):
            return None
        match = re.search(r"(\d+)\s*ml", str(value))
        return int(match.group(1)) if match else None

    feed_df["Volume_ml"] = feed_df["EndCondition"].apply(extract_ml)
    feed_df = feed_df[feed_df["Volume_ml"].notnull()]
    feed_df.sort_values("StartTime", inplace=True)

    return feed_df[["StartTime", "StartCondition", "Volume_ml"]]



def analyze_feed_volume(days: Optional[int] = None) -> dict:
    feed_df = preprocess_feed_data()

    # 若无喂奶数据，直接返回提示
    if feed_df.empty:
        return {
            "summary": "没有喂奶记录。",
            "total_volume_ml": 0,
            "average_volume_per_feed": 0,
            "feeds_per_day": 0,
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    now = feed_df["StartTime"].max()

    # 如果指定了天数，筛选最近 N 天的数据
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date]
    else:
        recent_df = feed_df

    if recent_df.empty:
        return {
            "summary": f"最近 {days} 天内没有喂奶记录。" if days else "没有喂奶记录。",
            "total_volume_ml": 0,
            "average_volume_per_feed": 0,
            "feeds_per_day": 0,
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    total_volume = recent_df["Volume_ml"].sum()
    feed_count = recent_df.shape[0]
    avg_per_feed = recent_df["Volume_ml"].mean()
    feeds_per_day = feed_count / days if days else feed_count

    if avg_per_feed < 90:
        rec = "宝宝每次吃奶量偏少，建议关注是否存在吸吮无力或间隔过短的情况。"
    elif avg_per_feed > 150:
        rec = "宝宝每次吃奶量偏多，留意是否有呕吐或胀气现象。"
    else:
        rec = "宝宝吃奶量处于健康范围，可以继续维持当前喂养策略。"

    return {
        "summary": f"过去 {days} 天共记录 {feed_count} 次喂奶，总摄入 {total_volume} ml，平均每次 {avg_per_feed:.1f} ml。" if days else f"共记录 {feed_count} 次喂奶，总摄入 {total_volume} ml，平均每次 {avg_per_feed:.1f} ml。",
        "total_volume_ml": total_volume,
        "average_volume_per_feed": round(avg_per_feed, 1),
        "feeds_per_day": round(feeds_per_day, 2),
        "recommendation": rec
    }

from google.adk.agents import Agent
feed_volume_agent = Agent(
    name="feed_volume_analyst",
    model="gemini-2.0-flash",
    description="An agent that analyzes baby feeding data over a specified number of days.",
    instruction="""
    You are a feeding volume analyst agent responsible for analyzing feeding volume patterns.
    You can provide insights into total volume, frequency, and suggestions based on baby's milk intake.
    
    Use the analyze_feed_volume_tool to generate your report.
    """,
    tools=[analyze_feed_volume],
)