from typing import Optional, Dict, Any
import pandas as pd

DATA_PATH = "/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv"

def preprocess_diaper_timing_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    diaper_df = df[df["Type"] == "Diaper"].copy()
    diaper_df["StartTime"] = pd.to_datetime(diaper_df["StartTime"])
    return diaper_df

def analyze_diaper_timing(days: Optional[int] = None, bins: Optional[int] = 6) -> Dict[str, Any]:
    """
    分析一天中尿布更换的时间分布，bins为一天分成的时间段数（如6为每4小时一个段）。
    """
    diaper_df = preprocess_diaper_timing_data()
    if diaper_df.empty:
        return {
            "summary": "没有尿布更换记录，无法分析时间分布。",
            "timing_distribution": None,
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
            "timing_distribution": None,
            "recommendation": "请确保数据中包含尿布更换信息。"
        }

    # 提取小时
    recent_df["Hour"] = recent_df["StartTime"].dt.hour + recent_df["StartTime"].dt.minute / 60

    # 分时间段统计
    bin_edges = [24 * i / bins for i in range(bins + 1)]
    bin_labels = [f"{int(bin_edges[i]):02d}:00-{int(bin_edges[i+1]):02d}:00" for i in range(bins)]
    recent_df["TimePeriod"] = pd.cut(recent_df["Hour"], bins=bin_edges, labels=bin_labels, right=False, include_lowest=True)

    timing_distribution = recent_df["TimePeriod"].value_counts().sort_index().to_dict()

    # 判断是否集中
    max_period = max(timing_distribution, key=timing_distribution.get)
    max_count = timing_distribution[max_period]
    total = sum(timing_distribution.values())
    concentration = max_count / total if total else 0

    if concentration > 0.4:
        pattern = f"更换时间主要集中在 {max_period}。"
    else:
        pattern = "更换时间分布较为均匀。"

    summary = (
        f"最近 {days if days else '全部'} 天内，尿布更换时间分布如下：{timing_distribution}。{pattern}"
    )

    return {
        "summary": summary,
        "timing_distribution": timing_distribution,
        "recommendation": "关注是否存在更换时间集中或不规律的情况，合理安排护理。"
    }

from google.adk.agents import Agent

diaper_timing_agent = Agent(
    name="diaper_timing_agent",
    model="gemini-2.0-flash",
    description="An agent that analyzes the time-of-day distribution of diaper changes and detects patterns.",
    instruction="""
    You are a diaper timing analysis agent.
    Your task is to analyze the distribution of diaper changes throughout the day (e.g., whether they are concentrated in certain periods or regular).
    Use the analyze_diaper_timing tool to generate your report.
    """,
    tools=[analyze_diaper_timing],
)