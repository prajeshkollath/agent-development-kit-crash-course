from typing import Optional, Dict, Any
import pandas as pd
import re

from beebi.data.db_utils import fetch_activity_data  # 使用数据库工具获取数据

def preprocess_diaper_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
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
    return df

def analyze_diaper_frequency(
    days: Optional[int] = None,
    by_user: bool = False,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    diaper_df = preprocess_diaper_data(days=days, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "没有尿布更换记录，无法分析。",
            "details": None,
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
            "details": None,
            "recommendation": "请确保数据中包含尿布更换信息。"
        }

    # 按用户统计
    group_fields = ["CustomerID"] if by_user else []
    recent_df["Date"] = recent_df["StartTime"].dt.date

    freq_stats = recent_df.groupby(group_fields + ["Date"]).size().reset_index(name="ChangeCount")
    if group_fields:
        avg_per_day = freq_stats.groupby(group_fields)["ChangeCount"].mean().reset_index(name="AvgChangePerDay")
        avg_per_day_records = avg_per_day.to_dict(orient="records")
        summary = f"最近 {days if days else '全部'} 天内，平均每日更换尿布 {avg_per_day['AvgChangePerDay'].mean():.1f} 次。（已分用户统计）"
    else:
        avg = freq_stats["ChangeCount"].mean()
        avg_per_day_records = [{"AvgChangePerDay": avg}]
        summary = f"最近 {days if days else '全部'} 天内，平均每日更换尿布 {avg:.1f} 次。"

    # 统计pee/poo类型分布
    pee_stats = recent_df["Pee"].value_counts(dropna=True).to_dict()
    poo_stats = recent_df["Poo"].value_counts(dropna=True).to_dict()

    if by_user:
        summary += "（已分用户统计）"

    return {
        "summary": summary,
        "avg_per_day": avg_per_day_records,
        "pee_stats": pee_stats,
        "poo_stats": poo_stats,
        "recommendation": "建议根据更换频率和尿便量调整护理计划。"
    }

from google.adk.agents import Agent

diaper_frequency_agent = Agent(
    name="diaper_frequency_analyst",
    model="gemini-2.0-flash",
    description="An agent that analyzes diaper change frequency and pee/poo amount trends.",
    instruction="""
    You are a diaper frequency analyst agent.
    Your task is to analyze the frequency of diaper changes (daily, by period, by user) and the distribution of pee/poo amounts (small, medium, big).
    Use the analyze_diaper_frequency tool to generate your report.
    """,
    tools=[analyze_diaper_frequency],
)