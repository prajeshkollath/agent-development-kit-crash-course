from typing import Optional, Dict, Any
import pandas as pd
import re

DATA_PATH = "/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv"

def preprocess_diaper_type_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    diaper_df = df[df["Type"] == "Diaper"].copy()
    diaper_df["StartTime"] = pd.to_datetime(diaper_df["StartTime"])

    # 提取尿量和便量类型
    def extract_condition(cond, kind):
        if pd.isna(cond):
            return None
        cond = str(cond).lower()
        match = re.search(rf"{kind}:(small|medium|big)", cond)
        return match.group(1) if match else None

    diaper_df["PeeType"] = diaper_df["EndCondition"].apply(lambda x: extract_condition(x, "pee"))
    diaper_df["PooType"] = diaper_df["EndCondition"].apply(lambda x: extract_condition(x, "poo"))
    return diaper_df

def analyze_diaper_type(days: Optional[int] = None) -> Dict[str, Any]:
    diaper_df = preprocess_diaper_type_data()
    if diaper_df.empty:
        return {
            "summary": "没有尿布内容记录，无法分析尿/便类型。",
            "pee_stats": None,
            "poo_stats": None,
            "recommendation": "请确保有尿布内容数据。"
        }

    now = diaper_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = diaper_df["StartTime"].min()

    recent_df = diaper_df[diaper_df["StartTime"] >= start_date].copy()
    if recent_df.empty:
        return {
            "summary": f"最近 {days if days else '全部'} 天内无尿布内容记录。",
            "pee_stats": None,
            "poo_stats": None,
            "recommendation": "请确保数据中包含尿布内容信息。"
        }

    # 统计pee/poo类型分布
    pee_stats = recent_df["PeeType"].value_counts(dropna=True).to_dict()
    poo_stats = recent_df["PooType"].value_counts(dropna=True).to_dict()

    summary = (
        f"最近 {days if days else '全部'} 天内，"
        f"有尿的记录 {sum(pee_stats.values())} 次，"
        f"有便便的记录 {sum(poo_stats.values())} 次。"
    )

    return {
        "summary": summary,
        "pee_stats": pee_stats,
        "poo_stats": poo_stats,
        "recommendation": "关注尿/便类型分布，及时发现异常。"
    }

from google.adk.agents import Agent

diaper_type_analysis_agent = Agent(
    name="diaper_type_analysis_agent",
    model="gemini-2.0-flash",
    description="An agent that analyzes diaper content types: whether there is pee or poo, and their levels (small/medium/big).",
    instruction="""
    You are a diaper type analysis agent.
    Your task is to analyze whether each diaper change contains pee or poo, and their respective levels (small, medium, big).
    Use the analyze_diaper_type tool to generate your report.
    """,
    tools=[analyze_diaper_type],
)