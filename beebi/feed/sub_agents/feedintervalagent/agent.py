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


import pandas as pd
from typing import Optional

def analyze_feed_intervals(days: Optional[int] = None) -> dict:
    feed_df = preprocess_feed_data()

    # 若无喂奶数据，直接返回提示
    if feed_df.empty:
        return {
            "summary": "没有喂奶记录，无法计算间隔。",
            "average_interval_hours": None,
            "min_interval_hours": None,
            "max_interval_hours": None,
            "std_dev_hours": None,
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    now = feed_df["StartTime"].max()

    # 如果指定了天数，筛选最近 N 天的数据
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()

    recent_df.sort_values("StartTime", inplace=True)

    if recent_df.shape[0] < 2:
        return {
            "summary": f"最近 {days} 天内喂奶记录过少，无法计算间隔。" if days else "喂奶记录过少，无法计算间隔。",
            "average_interval_hours": None,
            "min_interval_hours": None,
            "max_interval_hours": None,
            "std_dev_hours": None,
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }

    # 计算间隔（单位：小时）
    intervals = recent_df["StartTime"].diff().dropna().dt.total_seconds() / 3600
    avg_interval = intervals.mean()
    min_interval = intervals.min()
    max_interval = intervals.max()
    std_dev = intervals.std()

    # 简单规律性分析
    if std_dev < 1:
        pattern = "喂奶时间间隔非常规律。"
    elif std_dev > 3:
        pattern = "喂奶间隔波动较大，可能存在计划不一致或记录疏漏。"
    else:
        pattern = "喂奶间隔有一定波动，基本正常。"

    return {
        "summary": f"最近 {days} 天内平均每 {avg_interval:.1f} 小时喂一次奶（最短 {min_interval:.1f} 小时，最长 {max_interval:.1f} 小时）。" if days else f"平均每 {avg_interval:.1f} 小时喂一次奶（最短 {min_interval:.1f} 小时，最长 {max_interval:.1f} 小时）。",
        "average_interval_hours": round(avg_interval, 1),
        "min_interval_hours": round(min_interval, 1),
        "max_interval_hours": round(max_interval, 1),
        "std_dev_hours": round(std_dev, 2),
        "recommendation": pattern
    }


from google.adk.agents import Agent

feed_interval_agent = Agent(
    name="feed_interval_agent",
    model="gemini-2.0-flash",
    description="An agent that analyzes baby feeding intervals over a specified number of days.",
    instruction="""
    You are a feeding interval analyst agent responsible for analyzing the timing between feeding sessions.
    You help detect patterns such as overly frequent feeding, long gaps between sessions, or irregular schedules.

    Use the analyze_feed_intervals tool to generate your report. Your output should be clear, concise, and insightful for parents or caregivers.
    """,
    tools=[analyze_feed_intervals],
)
