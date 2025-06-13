from typing import Optional, Dict, Any
import pandas as pd
import re

from beebi.data.db_utils import fetch_activity_data

def preprocess_diaper_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    """
    根据传入的 days 和 customer_id，从数据库获取指定天数内的尿布原始数据。
    """
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Diaper", since_days=since_days)
    if df.empty:
        return df
    df["StartTime"] = pd.to_datetime(df["StartTime"])

    # 提取尿量和便量
    def extract_condition(cond, kind):
        if pd.isna(cond):
            return None
        cond = str(cond).lower()
        match = re.search(rf"{kind}:(small|medium|big)", cond)
        return match.group(1) if match else None

    df["Pee"] = df["EndCondition"].apply(lambda x: extract_condition(x, "pee"))
    df["Poo"] = df["EndCondition"].apply(lambda x: extract_condition(x, "poo"))
    df = df.sort_values("StartTime")
    return df

def analyze_diaper_alert(
    days: Optional[int] = None,
    max_interval_hours: float = 5.0,
    big_poo_threshold: int = 2,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    识别不正常的排泄频率或类型，如连续多次 big poo，超过时间未换等。
    """
    diaper_df = preprocess_diaper_data(days=days, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "没有尿布更换记录，无法进行异常提醒分析。",
            "alerts": [],
            "recommendation": "请确保有尿布数据。"
        }

    now = diaper_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = diaper_df["StartTime"].min()
    recent_df = diaper_df[diaper_df["StartTime"] >= start_date].copy()
    if recent_df.empty:
        return {
            "summary": f"最近 {days if days else '全部'} 天内无尿布更换记录。",
            "alerts": [],
            "recommendation": "请确保数据中包含尿布更换信息。"
        }

    alerts = []

    # 检查连续多次 big poo
    poo_types = recent_df["Poo"].tolist()
    count = 0
    for i, val in enumerate(poo_types):
        if val == "big":
            count += 1
            if count >= big_poo_threshold:
                alerts.append(f"检测到连续 {count} 次大便为 big poo（第 {i+1} 次）。")
        else:
            count = 0

    # 检查更换间隔是否过长
    recent_df = recent_df.sort_values("StartTime")
    recent_df["NextStartTime"] = recent_df["StartTime"].shift(-1)
    recent_df["Interval"] = (recent_df["NextStartTime"] - recent_df["StartTime"]).dt.total_seconds() / 3600
    long_intervals = recent_df[recent_df["Interval"] > max_interval_hours]
    for idx, row in long_intervals.iterrows():
        alerts.append(
            f"{row['StartTime']} 至 {row['NextStartTime']} 更换间隔超过 {max_interval_hours} 小时（实际 {row['Interval']:.1f} 小时）。"
        )

    summary = (
        "未发现异常。" if not alerts
        else f"发现 {len(alerts)} 条异常提醒。"
    )

    return {
        "summary": summary,
        "alerts": alerts,
        "recommendation": "请关注异常提醒，及时调整护理计划。"
    }

from google.adk.agents import Agent

diaper_alert_agent = Agent(
    name="diaper_alert_agent",
    model="gemini-2.0-flash",
    description="An agent that detects abnormal diaper change patterns, such as consecutive big poos or excessive intervals between changes.",
    instruction="""
    You are a diaper alert agent.
    Your task is to identify abnormal excretion patterns, such as consecutive big poos or excessive time intervals without a change, to help with parent reminders.
    Use the analyze_diaper_alert tool to generate your report.
    """,
    tools=[analyze_diaper_alert],
)