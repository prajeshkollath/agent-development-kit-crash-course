from typing import Optional
import pandas as pd
import re
from typing import Optional

DATA_PATH = "/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv"

def preprocess_feed_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    # 保留 Feed 类型
    feed_df = df[df["Type"] == "Feed"].copy()

    # 转换时间格式
    feed_df["StartTime"] = pd.to_datetime(feed_df["StartTime"])

    # 提取 ml 数值
    def extract_ml(value):
        if pd.isna(value):
            return None
        match = re.search(r"(\d+)\s*ml", str(value))
        return int(match.group(1)) if match else None

    feed_df["Volume_ml"] = feed_df["EndCondition"].apply(extract_ml)
    feed_df = feed_df[feed_df["Volume_ml"].notnull()]
    feed_df.sort_values("StartTime", inplace=True)

    # 提取 FeedType 字段（从 StartCondition 字段标准化）
    def extract_feed_type(cond):
        if pd.isna(cond):
            return None
        cond = str(cond).strip().lower()
        if "formula" in cond:
            return "FormulaMilk"
        if "breast" in cond:
            return "BreastMilk"
        return None

    feed_df["FeedType"] = feed_df["StartCondition"].apply(extract_feed_type)

    return feed_df[["StartTime", "StartCondition", "Volume_ml", "FeedType"]]

def analyze_feed_type_ratio(days: Optional[int] = None) -> dict:
    feed_df = preprocess_feed_data()

    if feed_df.empty or "FeedType" not in feed_df.columns:
        return {
            "summary": "没有喂奶记录，无法分析母乳与配方奶比例。",
            "breast_milk_ratio": None,
            "formula_milk_ratio": None,
            "recommendation": "请确保有喂奶数据。"
        }

    now = feed_df["StartTime"].max()
    if days is not None:
        start_date = now - pd.Timedelta(days=days)
    else:
        start_date = feed_df["StartTime"].min()

    recent_df = feed_df[(feed_df["StartTime"] >= start_date) & (feed_df["FeedType"].notnull())].copy()
    
    if recent_df.empty:
        return {
            "summary": f"最近 {days if days else '全部'} 天内无喂奶类型记录，无法分析母乳与配方奶比例。",
            "breast_milk_ratio": None,
            "formula_milk_ratio": None,
            "recommendation": "请确保喂奶记录中包含母乳或配方奶信息。"
        }

    # 统计母乳与配方奶的次数和占比
    type_counts = recent_df["FeedType"].value_counts()
    total_feeds = type_counts.sum()

    breast_milk_count = type_counts.get("BreastMilk", 0)
    formula_milk_count = type_counts.get("FormulaMilk", 0)

    breast_milk_ratio = breast_milk_count / total_feeds if total_feeds else 0
    formula_milk_ratio = formula_milk_count / total_feeds if total_feeds else 0

    # 趋势分析
    recent_df['Date'] = recent_df['StartTime'].dt.date
    daily_ratio = recent_df.groupby('Date')['FeedType'].apply(
        lambda x: (x == "BreastMilk").sum() / len(x)
    )
    trend = "母乳比例变化不明显。"
    if len(daily_ratio) >= 2:
        if daily_ratio.iloc[-1] > daily_ratio.iloc[0]:
            trend = "母乳比例呈上升趋势。"
        elif daily_ratio.iloc[-1] < daily_ratio.iloc[0]:
            trend = "母乳比例呈下降趋势。"

    return {
        "summary": f"最近 {days if days else '全部'} 天内母乳占比约为 {breast_milk_ratio:.0%}，配方奶占比约为 {formula_milk_ratio:.0%}。{trend}",
        "breast_milk_ratio": round(breast_milk_ratio, 2),
        "formula_milk_ratio": round(formula_milk_ratio, 2),
        "recommendation": "根据喂养比例合理调整混合喂养策略。"
    }


from google.adk.agents import Agent

feed_type_agent = Agent(
    name="feed_type_analyst",
    model="gemini-2.0-flash",
    description="An agent that analyzes the ratio and trends of breast milk versus formula milk usage.",
    instruction="""
    You are a feed type analyst agent.
    Your task is to analyze the proportion and trends of breast milk and formula milk feeding over a specified period.
    Provide insights to guide mixed feeding strategies.
    
    Use the analyze_feed_type_ratio tool to generate your report.
    """,
    tools=[analyze_feed_type_ratio],
)
