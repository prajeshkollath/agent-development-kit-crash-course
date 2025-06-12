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
    
    # 时间格式化
    df["RecordDate"] = pd.to_datetime(df["RecordDate"])
    
    # 数值提取（去除单位）
    df["Weight"] = df["Weight"].apply(extract_number)
    df["Height"] = df["Height"].apply(extract_number)
    df["Head"] = df["Head"].apply(extract_number)
    
    # 百分位处理（空值转为 None）
    df["Weight_Percentage"] = pd.to_numeric(df["Weight_Percentage"], errors='coerce')
    df["Height_Percentage"] = pd.to_numeric(df["Height_Percentage"], errors='coerce')
    df["Head_Percentage"] = pd.to_numeric(df["Head_Percentage"], errors='coerce')
    
    # 按时间排序
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

    # 可选：筛选最近N天
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
            # 检查高风险
            if curr < 3:
                high_risk = True
            # 检查百分位掉落
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

growth_anomaly_detector = Agent(
    name="growth_anomaly_detector",
    model="gemini-2.0-flash",
    description="An agent that detects growth anomalies such as percentile drops or persistent low percentiles.",
    instruction="""
    You are a growth anomaly detection agent. Analyze the baby's growth percentiles and identify any significant drops (≥10) or persistent values below the 3rd percentile.
    Use the analyze_growth_anomalies tool to generate your report. Output should be clear, concise, and actionable for caregivers.
    """,
    tools=[analyze_growth_anomalies],
)