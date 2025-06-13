import pandas as pd
import re
from typing import Optional, Dict, Any
import numpy as np

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

def analyze_feed_consistency(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    feed_df = preprocess_feed_data(days=days, customer_id=customer_id)
    if feed_df.empty:
        return {
            "summary": "没有喂奶记录。",
            "time_variability_cv": None,
            "volume_variability_cv": None,
            "time_pattern": None,
            "volume_pattern": None,
            "recommendation": "请确认是否有数据缺失或未及时记录。"
        }
    now = feed_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
        recent_df = feed_df[feed_df["StartTime"] >= start_date].copy()
    else:
        recent_df = feed_df.copy()
    recent_df = recent_df.dropna(subset=["StartTime", "Volume_ml"])
    recent_df.sort_values("StartTime", inplace=True)
    if recent_df.empty or recent_df.shape[0] < 2:
        return {
            "summary": f"最近 {days} 天内喂奶记录不足，无法计算波动。" if days else "喂奶记录不足，无法计算波动。",
            "time_variability_cv": None,
            "volume_variability_cv": None,
            "time_pattern": None,
            "volume_pattern": None,
            "recommendation": "请确认数据完整性。"
        }
    # 计算喂奶时间间隔（小时）
    intervals = recent_df["StartTime"].diff().dt.total_seconds().dropna() / 3600
    # 计算喂奶量（Volume_ml 字段，单位ml）
    volumes = recent_df["Volume_ml"].dropna()
    # 计算变异系数（CV = 标准差 / 平均）衡量波动性
    time_cv = intervals.std() / intervals.mean() if intervals.mean() != 0 else np.nan
    volume_cv = volumes.std() / volumes.mean() if volumes.mean() != 0 else np.nan
    # 评估时间波动
    if time_cv < 0.2:
        time_pattern = "喂奶时间间隔非常规律"
    elif time_cv > 0.5:
        time_pattern = "喂奶时间间隔波动较大，存在不规律情况"
    else:
        time_pattern = "喂奶时间间隔有一定波动，基本正常"
    # 评估喂奶量波动
    if volume_cv < 0.2:
        volume_pattern = "喂奶量波动较小，较为稳定"
    elif volume_cv > 0.5:
        volume_pattern = "喂奶量波动较大，可能存在喂养量不稳定"
    else:
        volume_pattern = "喂奶量有一定波动，属于正常范围"
    # 综合建议
    recommendation = (
        f"时间波动情况：{time_pattern}；喂奶量波动情况：{volume_pattern}。"
        "若存在较大波动，建议观察宝宝状态及父母喂养习惯，必要时咨询儿科医生。"
    )
    return {
        "summary": f"最近 {days} 天内喂奶时间和喂奶量波动分析。" if days else "喂奶时间和喂奶量波动分析。",
        "time_variability_cv": round(time_cv, 3) if not np.isnan(time_cv) else None,
        "volume_variability_cv": round(volume_cv, 3) if not np.isnan(volume_cv) else None,
        "time_pattern": time_pattern,
        "volume_pattern": volume_pattern,
        "recommendation": recommendation
    }

from google.adk.agents import Agent

feed_consistency_agent = Agent(
    name="feed_consistency_analyst",
    model="gemini-2.0-flash",
    description="An agent that analyzes the consistency of feeding times and volumes to detect regularity or instability.",
    instruction="""
    You are a feed consistency analyst agent.
    Your task is to analyze the variability of feeding times and feeding volumes over a given period.
    Identify whether the feeding pattern is regular or shows instability that might indicate baby's discomfort or feeding habits issues.
    Use the analyze_feed_consistency tool to generate your report.
    """,
    tools=[analyze_feed_consistency],
)
