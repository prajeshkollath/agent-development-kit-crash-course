import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def analyze_sleep_sessions(days: Optional[int] = None) -> dict:
    """
    分析睡眠数据，返回关键统计信息。
    仅包含 Type 为 'Sleep' 的记录。
    支持根据最近 N 天的数据分析，默认分析全部数据。
    """
    try:
        data_path = "/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv"
        df = pd.read_csv(data_path)
        
        # 只保留类型为 Sleep 的记录
        df = df[df["Type"] == "Sleep"].copy()

        # 若无 Sleep 数据，直接返回提示
        if df.empty:
            return {"status": "success", "report": "No sleep data found."}

            # 时间字段转换
        df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")
        df["EndTime"] = pd.to_datetime(df["EndTime"], errors="coerce")

            # 处理缺失或错误数据
        df = df.dropna(subset=["StartTime", "EndTime", "Duration"])

            # 如果指定了天数，筛选最近 N 天的数据
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df["StartTime"] >= cutoff_date]

        if df.empty:
            return {
                "status": "success",
                "report": f"No sleep data found for the last {days} days." if days else "No valid sleep data found."
            }

        # 计算睡眠时长小时数（Duration 是分钟）
        df["DurationHours"] = df["Duration"] / 60.0

        # 按日期统计每日睡眠总时长
        df["Date"] = df["StartTime"].dt.date
        daily_sleep = df.groupby("Date")["DurationHours"].sum().reset_index()

        total_days = daily_sleep["Date"].nunique()
        total_sessions = len(df)
        total_duration_hours = df["DurationHours"].sum()

        average_per_day = round(total_duration_hours / total_days, 2)
        average_per_session = round(df["Duration"].mean(), 2)

        # 睡眠质量分布，poor < 6h，good 6-8h，rich > 8h
        df["Quality"] = df["DurationHours"].apply(
            lambda h: "Poor" if h < 6 else ("Rich" if h > 8 else "Good")
        )
        quality_counts = df["Quality"].value_counts().to_dict()

        return {
            "status": "success",
            "report": {
                "days_analyzed": total_days,
                "total_sessions": total_sessions,
                "avg_hours_per_day": average_per_day,
                "avg_duration_per_session_minutes": average_per_session,
                "sleep_quality_distribution": quality_counts
            }
        }

    except Exception as e:
        return {"status": "error", "error_message": str(e)}
    
    
from google.adk.agents import Agent
# 定义睡眠分析Agent
sleep_analysis_agent = Agent(
    name="sleep_analysis_agent",
    model="gemini-2.0-flash",
    description="Analyzes and summarizes user sleep session data.",
    instruction=
    "You are the main Sleep Analysis Agent. Your job is to summarize sleep data using the tool 'analyze_sleep_sessions'. "
    "Use this tool to process session count, average duration, and sleep quality trends. "
    "You do not handle greetings, farewells, or unrelated topics. "
    "Always call the tool to generate reports. Do not generate reports by yourself."
    ,
    tools=[analyze_sleep_sessions]
)

