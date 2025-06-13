import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from beebi.data.db_utils import fetch_activity_data  # 使用数据库工具获取数据

def preprocess_sleep_data(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> pd.DataFrame:
    since_days = days if days is not None else 365
    cid = customer_id if customer_id is not None else 10
    df = fetch_activity_data(customer_id=cid, activity_type="Sleep", since_days=since_days)
    if df.empty:
        return df
    # 转换时间和数值类型
    df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")
    df["Duration"] = pd.to_numeric(df["Duration"], errors="coerce")
    # 只保留有效记录
    df = df.dropna(subset=["StartTime", "Duration"])
    # 只保留类型为 Sleep 的记录
    if "Type" in df.columns:
        df = df[df["Type"] == "Sleep"].copy()
    df = df.sort_values("StartTime")
    return df

def analyze_sleep_patterns(
    days: Optional[int] = None,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    try:
        sleep_df = preprocess_sleep_data(days=days, customer_id=customer_id)
        if sleep_df.empty:
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

        # 只分析最近 N 天的数据
        if days is not None:
            cutoff_date = datetime.now().date() - timedelta(days=days)
            sleep_df = sleep_df[sleep_df["StartTime"].dt.date >= cutoff_date]

        if sleep_df.empty:
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

        # 计算 StartHour = 小时 + 分钟/60
        sleep_df["StartHour"] = sleep_df["StartTime"].dt.hour + sleep_df["StartTime"].dt.minute / 60.0

        # 时间段划分
        def classify_segment(hour):
            if 6 <= hour < 12:
                return "Morning"
            elif 12 <= hour < 18:
                return "Afternoon"
            elif 18 <= hour < 24:
                return "Evening"
            else:
                return "Overnight"

        sleep_df["TimeSegment"] = sleep_df["StartHour"].apply(classify_segment)
        segment_counts = sleep_df["TimeSegment"].value_counts().to_dict()

        # 睡眠一致性计算
        sleep_onsets = sleep_df["StartHour"]
        drift = round(sleep_onsets.max() - sleep_onsets.min(), 2) if not sleep_onsets.empty else None
        duration_std = round(sleep_df["Duration"].std(), 2) if not sleep_df["Duration"].empty else None

        # 睡眠模式识别
        long_night_sleeps = sleep_df[(sleep_df["TimeSegment"] == "Overnight") & (sleep_df["Duration"] >= 240)]
        naps = sleep_df[(sleep_df["TimeSegment"].isin(["Morning", "Afternoon"])) & (sleep_df["Duration"] < 120)]

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
        import traceback
        print("Sleep pattern analysis error:", e)
        traceback.print_exc()
        return {"status": "error", "error_message": str(e)}


from google.adk.agents import Agent

sleep_pattern_agent = Agent(
    name="sleep_pattern_agent",
    model="gemini-2.0-flash",
    description="Recognizes and analyzes sleep time patterns, segmentations, and consistency.",
    instruction=(
        "You are the Sleep Pattern Recognition Agent. "
        "Your job is to recognize and analyze sleep time patterns, segmentations, and consistency using the tool 'analyze_sleep_patterns'. "
        "Classify sleep sessions by time (morning, afternoon, evening, overnight), "
        "analyze sleep patterns (nap frequency, long night sleep), and compute consistency metrics "
        "such as sleep onset drift and duration variability. "
        "Always use the tool 'analyze_sleep_patterns' to provide reports. "
        "Do not generate sleep reports manually. "
        "Do not answer greetings, farewells, or unrelated questions."
    ),
    tools=[analyze_sleep_patterns]
)
