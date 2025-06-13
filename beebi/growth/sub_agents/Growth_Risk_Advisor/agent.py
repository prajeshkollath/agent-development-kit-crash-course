import pandas as pd
import re
from typing import Optional, Dict, Any

DATA_PATH = "/workspaces/agent-development-kit-crash-course/beebi/data/growthdata.csv"

def extract_number(value: str) -> Optional[float]:
    if pd.isna(value) or value == 0.0:
        return None
    try:
        return float(re.sub(r"[^\d.]+", "", str(value)))
    except:
        return None

def preprocess_growth_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["RecordDate"] = pd.to_datetime(df["RecordDate"])
    df["Weight"] = df["Weight"].apply(extract_number)
    df["Height"] = df["Height"].apply(extract_number)
    df["Head"] = df["Head"].apply(extract_number)
    df["Weight_Percentage"] = pd.to_numeric(df["Weight_Percentage"], errors='coerce')
    df["Height_Percentage"] = pd.to_numeric(df["Height_Percentage"], errors='coerce')
    df["Head_Percentage"] = pd.to_numeric(df["Head_Percentage"], errors='coerce')
    df = df.sort_values("RecordDate")
    return df

def analyze_growth_anomalies(days: Optional[int] = None) -> Dict[str, Any]:
    df = preprocess_growth_data()
    if df.empty or df.shape[0] < 2:
        return {
            "summary": "成长记录过少，无法分析异常。",
            "anomalies": [],
            "high_risk": False,
            "recommendation": "请补充更多成长记录。"
        }

    if days is not None:
        latest = df["RecordDate"].max()
        start_date = latest - pd.Timedelta(days=days)
        df = df[df["RecordDate"] >= start_date]

    df = df.sort_values("RecordDate").reset_index(drop=True)
    anomalies = []
    high_risk = False

    for metric in ["Weight_Percentage", "Height_Percentage"]:
        prev = None
        for idx, row in df.iterrows():
            curr = row[metric]
            date = row["RecordDate"]
            if pd.isna(curr):
                continue
            if curr < 3:
                high_risk = True
            if prev is not None and not pd.isna(prev):
                drop = prev - curr
                if drop >= 10:
                    anomalies.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "metric": metric,
                        "drop": round(drop, 1),
                        "from": round(prev, 1),
                        "to": round(curr, 1),
                        "type": "percentile_drop"
                    })
            prev = curr

    summary = []
    if anomalies:
        summary.append(f"检测到 {len(anomalies)} 次百分位急剧下降（≥10）。")
    if high_risk:
        summary.append("有记录持续低于第3百分位，高风险。")
    if not summary:
        summary.append("未发现明显成长异常。")

    return {
        "summary": " ".join(summary),
        "anomalies": anomalies,
        "high_risk": high_risk,
        "recommendation": (
            "建议关注成长曲线，若多次掉落或持续低于第3百分位，请及时咨询儿科医生。"
            if anomalies or high_risk else "成长趋势正常，请继续定期记录。"
        )
    }

from google.adk.agents import Agent

growth_risk_advisor = Agent(
    name="growth_risk_advisor",
    model="gemini-2.0-flash",
    description="基于成长数据，检测成长风险（如百分位急剧下降、持续低于第3百分位等），为家长提供建议。",
    instruction="""
    你是成长风险分析助手。请分析宝宝的成长百分位，识别任何显著下降（≥10）或持续低于第3百分位的情况。
    使用 analyze_growth_anomalies 工具生成报告，输出应简明、清晰、可操作，便于家长理解和采取措施。
    """,
    tools=[analyze_growth_anomalies],
)

