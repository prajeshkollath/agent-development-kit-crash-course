import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

def analyze_sleep_patterns(days: Optional[int] = None) -> dict:
    try:
        df = pd.read_csv("/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv")

        # 只保留睡眠类型数据
        df = df[df["Type"] == "Sleep"].copy()

        # 检查必要列
        if "StartTime" not in df.columns or "Duration" not in df.columns:
            return {"status": "error", "error_message": "Missing StartTime or Duration column."}

        # 1. 解析 StartTime 为 datetime
        df["StartTime"] = pd.to_datetime(df["StartTime"])

        # 可选：只分析最近 N 天的数据
        if days is not None:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            df = df[df["StartTime"].dt.date >= cutoff_date]

        # 如果数据为空，提前返回
        if df.empty:
            return {
                "status": "success",
                "report": {
                    "segment_distribution": {},
                    "sleep_onset_drift": None,
                    "duration_std_dev": None,
                    "profile": "No sleep data available",
                    "naps_detected": 0,
                    "long_night_sleeps_detected": 0
                }
            }

        # 2. 计算 StartHour = 小时 + 分钟/60
        df["StartHour"] = df["StartTime"].dt.hour + df["StartTime"].dt.minute / 60.0

        # 3. 时间段划分
        def classify_segment(hour):
            if 6 <= hour < 12:
                return "Morning"
            elif 12 <= hour < 18:
                return "Afternoon"
            elif 18 <= hour < 24:
                return "Evening"
            else:
                return "Overnight"

        df["TimeSegment"] = df["StartHour"].apply(classify_segment)
        segment_counts = df["TimeSegment"].value_counts().to_dict()

        # 4. 睡眠一致性计算
        sleep_onsets = df["StartHour"]
        drift = round(sleep_onsets.max() - sleep_onsets.min(), 2)
        duration_std = round(df["Duration"].std(), 2)

        # 5. 睡眠模式识别
        long_night_sleeps = df[(df["TimeSegment"] == "Overnight") & (df["Duration"] >= 240)]
        naps = df[(df["TimeSegment"].isin(["Morning", "Afternoon"])) & (df["Duration"] < 120)]

        if len(long_night_sleeps) >= 5 and len(naps) >= 3:
            pattern = "Long night sleep with regular naps"
        elif len(naps) >= 3:
            pattern = "Frequent naps, fragmented sleep"
        elif len(long_night_sleeps) >= 5:
            pattern = "Consistent long night sleep"
        else:
            pattern = "Irregular sleep pattern"

        return {
            "status": "success",
            "report": {
                "segment_distribution": segment_counts,
                "sleep_onset_drift": drift,
                "duration_std_dev": duration_std,
                "profile": pattern,
                "naps_detected": len(naps),
                "long_night_sleeps_detected": len(long_night_sleeps)
            }
        }

    except Exception as e:
        return {"status": "error", "error_message": str(e)}



from google.adk.agents import Agent

sleep_pattern_agent = Agent(
    name="sleep_pattern_agent",
    model="gemini-2.0-flash",
    description="Recognizes and analyzes sleep time patterns, segmentations, and consistency.",
    instruction=(
        "You are the Sleep Pattern Recognition Agent. "
        "Your job is to Recognizes and analyzes sleep time patterns, segmentations, and consistency using the tool 'analyze_sleep_patterns'"
        "Your job is to classify sleep sessions by time (morning, afternoon, evening, overnight), "
        "analyze sleep patterns (nap frequency, long night sleep), and compute consistency metrics "
        "such as sleep onset drift and duration variability. "
        "Always use the tool 'analyze_sleep_patterns' to provide reports. "
        "Do not generate sleep reports manually. "
        "Do not answer greetings, farewells, or unrelated questions."
    ),
    tools=[analyze_sleep_patterns]
)
