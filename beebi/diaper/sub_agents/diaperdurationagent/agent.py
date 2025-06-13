from typing import Optional, Dict, Any
import pandas as pd

from beebi.data.db_utils import fetch_activity_data  # 使用数据库工具获取数据

def preprocess_diaper_duration_data(
    days: Optional[int] = None,
    by_user: bool = False,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    # 支持按用户过滤
    df = fetch_activity_data(
        customer_id=customer_id if customer_id is not None else 10,
        activity_type="Diaper",
        since_days=since_days
    )
    if df.empty:
        return df
    df["StartTime"] = pd.to_datetime(df["StartTime"])
    df = df.sort_values("StartTime")
    return df

def analyze_diaper_duration(
    days: Optional[int] = None,
    by_user: bool = False,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    计算每次尿布持续的时间（StartTime ~ 下一次 StartTime），分析平均更换间隔。
    """
    diaper_df = preprocess_diaper_duration_data(days=days, by_user=by_user, customer_id=customer_id)
    if diaper_df.empty:
        return {
            "summary": "没有尿布更换记录，无法分析更换间隔。",
            "interval_stats": None,
            "recommendation": "请确保有尿布数据。"
        }

    now = diaper_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = diaper_df["StartTime"].min()
    recent_df = diaper_df[diaper_df["StartTime"] >= start_date].copy()
    if recent_df.empty or len(recent_df) < 2:
        return {
            "summary": f"最近 {days if days else '全部'} 天内尿布更换记录不足，无法分析间隔。",
            "interval_stats": None,
            "recommendation": "请确保数据中包含足够的尿布更换信息。"
        }

    # 按用户分组或整体计算
    group_fields = ["CustomerID"] if by_user and "CustomerID" in recent_df.columns else []
    interval_stats = []

    if group_fields:
        for user, group in recent_df.groupby("CustomerID"):
            group = group.sort_values("StartTime")
            group["NextStartTime"] = group["StartTime"].shift(-1)
            group["Interval"] = (group["NextStartTime"] - group["StartTime"]).dt.total_seconds() / 3600
            intervals = group["Interval"].dropna()
            interval_stats.append({
                "CustomerID": user,
                "avg_interval_hours": round(intervals.mean(), 2) if not intervals.empty else None,
                "min_interval_hours": round(intervals.min(), 2) if not intervals.empty else None,
                "max_interval_hours": round(intervals.max(), 2) if not intervals.empty else None,
                "count": len(intervals)
            })
    else:
        recent_df = recent_df.sort_values("StartTime")
        recent_df["NextStartTime"] = recent_df["StartTime"].shift(-1)
        recent_df["Interval"] = (recent_df["NextStartTime"] - recent_df["StartTime"]).dt.total_seconds() / 3600
        intervals = recent_df["Interval"].dropna()
        interval_stats.append({
            "avg_interval_hours": round(intervals.mean(), 2) if not intervals.empty else None,
            "min_interval_hours": round(intervals.min(), 2) if not intervals.empty else None,
            "max_interval_hours": round(intervals.max(), 2) if not intervals.empty else None,
            "count": len(intervals)
        })

    summary = (
        f"最近 {days if days else '全部'} 天内，"
        f"平均每次尿布更换间隔约 {interval_stats[0]['avg_interval_hours']} 小时。"
        if interval_stats and interval_stats[0]['avg_interval_hours'] is not None
        else "无法计算有效的更换间隔。"
    )

    return {
        "summary": summary,
        "interval_stats": interval_stats,
        "recommendation": "关注更换间隔，避免间隔过长或过短。"
    }

from google.adk.agents import Agent

diaper_duration_agent = Agent(
    name="diaper_duration_agent",
    model="gemini-2.0-flash",
    description="An agent that analyzes the duration between diaper changes (intervals) and provides average interval statistics.",
    instruction="""
    You are a diaper duration analysis agent.
    Your task is to calculate the duration between each diaper change (from StartTime to the next StartTime), and analyze the average, minimum, and maximum intervals.
    Use the analyze_diaper_duration tool to generate your report.
    """,
    tools=[analyze_diaper_duration],
)