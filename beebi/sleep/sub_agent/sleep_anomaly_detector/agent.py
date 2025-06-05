import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def detect_sleep_anomalies(days: Optional[int] = None) -> dict:
    try:
        # 读取数据
        df = pd.read_csv("/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv")

        # 只保留 Type 为 Sleep 的记录
        df = df[df["Type"] == "Sleep"].copy()

        # 自动解析时间字段
        df["StartTime"] = pd.to_datetime(df["StartTime"])
        df["EndTime"] = pd.to_datetime(df["EndTime"])

        # 如果指定了天数，筛选最近 N 天的数据
        if days is not None:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            df = df[df["StartTime"].dt.date >= cutoff_date]

        # 如果数据为空，直接返回
        if df.empty:
            return {
                "status": "success",
                "report": {
                    "days_with_sleep_duration_jumps": [],
                    "missed_nap_days": [],
                    "note": "No sleep data found in the specified time range."
                }
            }

        # 提取日期和小时
        df["Date"] = df["StartTime"].dt.date
        df["StartHour"] = df["StartTime"].dt.hour

        # Step 1: 每日总睡眠时长（分钟）
        daily_sleep = df.groupby("Date")["Duration"].sum().reset_index()
        daily_sleep["SleepChange"] = daily_sleep["Duration"].diff()

        # 标记变动幅度 > 90分钟的日期
        large_changes = daily_sleep[abs(daily_sleep["SleepChange"]) > 90]
        large_change_days = large_changes["Date"].astype(str).tolist()

        # Step 2: Nap 探测（12pm–6pm 且 Duration ≤ 120min）
        df["IsNap"] = df["StartHour"].between(12, 17, inclusive="both") & (df["Duration"] <= 120)

        # 统计每一天 nap 的数量
        nap_counts = df[df["IsNap"]].groupby("Date").size()
        nap_avg = nap_counts.mean() if not nap_counts.empty else 0

        # 找出 nap 数量远低于平均的日期
        threshold = max(1, nap_avg * 0.5)
        missed_nap_days = nap_counts[nap_counts < threshold].index.astype(str).tolist()

        return {
            "status": "success",
            "report": {
                "days_with_sleep_duration_jumps": large_change_days,
                "missed_nap_days": missed_nap_days
            }
        }

    except Exception as e:
        return {"status": "error", "error_message": str(e)}



from google.adk.agents import Agent

sleep_anomaly_detector = Agent(
    name="sleep_anomaly_detector",
    model="gemini-2.0-flash",
    description="Detects sleep anomalies such as sudden changes in duration and missed naps.",
    instruction=(
        "You are a Sleep Anomaly Detection Agent. "
        "Use the 'detect_sleep_anomalies' tool to find days with large changes in sleep duration and missed naps "
        "based on historical nap patterns. Only use the tool to analyze; do not guess or summarize manually."
    ),
    tools=[detect_sleep_anomalies]
)
