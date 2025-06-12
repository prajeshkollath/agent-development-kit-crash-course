import pandas as pd
import re
from typing import Optional, Dict, Any

from beebi.data.db_utils import fetch_activity_data  # 使用数据库工具获取数据

def preprocess_feed_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Feed", since_days=since_days)
    if df.empty:
        return df

    # 转换时间格式
    df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")

    # 提取 ml 数值
    def extract_ml(value):
        if pd.isna(value):
            return None
        match = re.search(r"(\d+)\s*ml", str(value))
        return int(match.group(1)) if match else None

    df["Volume_ml"] = df["EndCondition"].apply(extract_ml)
    feed_df = df[df["Volume_ml"].notnull()].copy()
    feed_df = feed_df.dropna(subset=["StartTime"])
    feed_df.sort_values("StartTime", inplace=True)

    return feed_df[["StartTime", "StartCondition", "Volume_ml"]]

def analyze_feed_time_of_day(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)

    # 若无喂奶数据，直接返回提示
    if feed_df.empty:
        return {
            "summary": "没有喂奶记录。",
            "peak_periods": {},
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    now = feed_df["StartTime"].max()

    # 如果指定了天数，筛选最近 N 天的数据
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()

    if recent_df.empty:
        return {
            "summary": f"最近 {days} 天内没有喂奶记录。" if days else "没有喂奶记录。",
            "peak_periods": {},
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    # 定义时段函数
    def time_period(hour):
        if 6 <= hour < 10:
            return "早上"
        elif 10 <= hour < 14:
            return "中午"
        elif 17 <= hour < 20:
            return "晚上"
        else:
            return "夜间"

    recent_df["Period"] = recent_df["StartTime"].dt.hour.apply(time_period)

    # 统计各时段喂奶次数
    counts = recent_df["Period"].value_counts().to_dict()
    total_feeds = sum(counts.values())

    if total_feeds == 0:
        return {
            "summary": f"最近 {days} 天内喂奶数据不足，无法分析时段分布。",
            "peak_periods": {},
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    peak_periods = {period: round(count / total_feeds * 100, 1) for period, count in counts.items()}

    # 找出喂奶高峰时段
    peak_time = max(peak_periods, key=peak_periods.get)

    recommendation = (
        f"宝宝在{peak_time}时段喂奶次数最多，占比{peak_periods[peak_time]}%。"
        "建议根据高峰时段合理安排喂奶时间，避免宝宝过度饥饿或频繁喂养。"
        "夜间喂养若频繁，可考虑适当调整睡眠环境，减少干扰。"
    )

    return {
        "summary": f"最近 {days} 天内，喂奶时段分布（占比%）为：{peak_periods}",
        "peak_periods": peak_periods,
        "recommendation": recommendation
    }

from google.adk.agents import Agent

feed_time_of_day_agent = Agent(
    name="feed_time_of_day_analyst",
    model="gemini-2.0-flash",
    description="An agent that analyzes peak feeding times of day to help parents optimize feeding schedules.",
    instruction="""
    You analyze baby's feeding data to find peak feeding periods during the day: morning, noon, evening, and night.
    Your insights help parents optimize feeding rhythms and predict baby's hunger times.

    Use the analyze_feed_time_of_day tool to generate your analysis and recommendations.
    """,
    tools=[analyze_feed_time_of_day],
)
