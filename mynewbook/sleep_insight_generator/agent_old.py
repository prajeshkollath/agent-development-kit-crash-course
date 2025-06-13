import pandas as pd
from datetime import datetime
from typing import Optional
from google.adk.agents import LlmAgent


import pandas as pd
from typing import Optional
import re

def analyze_feed_data(days: Optional[int] = None) -> dict:
    """
    分析喂养数据，返回统计信息。
    可选参数 days 指定分析最近几天数据，默认分析全部。
    """

    try:
        data_path = "/workspaces/agent-development-kit-crash-course/beebi/sleep/data/data1.csv"
        df = pd.read_csv(data_path)
        # 只保留指定类型数据
        # 只保留类型为 Sleep 的记录 
        df = df[df["Type"] == "Sleep"].copy()

        # 若无 Sleep 数据，直接返回提示
        if df.empty:
            return {"status": "success", "report": "No sleep data found."}

            # 时间字段转换
        df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")
        

        # 直接在这里定义提取毫升数的逻辑
        def extract_volume_from_str(s):
            # 假设 EndCondition 中有形如 "50ml" 或 "50 ml" 的数字，我们提取数字部分
            if isinstance(s, str):
                match = re.search(r"(\d+)\s*ml", s.lower())
                if match:
                    return int(match.group(1))
            return 0

        # 应用提取函数
        df["Volume_ml"] = df["EndCondition"].apply(extract_volume_from_str)

        df = df.sort_values("StartTime")
        df["IntervalH"] = df["StartTime"].diff().dt.total_seconds() / 3600
        df["IsNight"] = df["Hour"].apply(lambda h: h < 6 or h >= 22)

        # 过滤最近days天数据
        if days is not None:
            cutoff_date = pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
            df = df[df["Date"] >= cutoff_date.date()]

        # 统计
        type_volume = df.groupby("StartCondition")["Volume_ml"].sum().to_dict()
        daily_volume = df.groupby("Date")["Volume_ml"].sum().to_dict()
        avg_interval = df["IntervalH"].mean()
        night_feed_count = int(df["IsNight"].sum())

        recent_feeds = df.tail(5)[["StartTime", "StartCondition", "Volume_ml", "IntervalH"]]
        recent_feeds_list = recent_feeds.to_dict(orient="records")
        for row in recent_feeds_list:
            row["StartTime"] = row["StartTime"].strftime("%Y-%m-%d %H:%M")

        return {
            "status": "success",
            "summary": {
                "volume_by_type": type_volume,
                "daily_volume": daily_volume,
                "average_interval_hours": round(avg_interval, 2) if avg_interval else None,
                "night_feed_count": night_feed_count
            },
            "recent_feeds": recent_feeds_list
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}



# feed_analytics_agent.py

root_agent = LlmAgent(
    name="feed_analytics_agent",
    model="gemini-2.0-flash",
    description="Analyzes baby feeding patterns, volumes, and intervals to generate a human-readable report.",
    instruction="""
You are a baby care expert who helps parents understand their baby's feeding habits.

Your job is to interpret structured feeding data and write a **clear, supportive feeding report** that any parent can understand easily.

You must begin by calling the function `analyze_feed_data()` to retrieve summarized feeding metrics.

Using the result, generate a natural-language **feeding insights report** that includes the following:

---

### 📊 What to Include:
1. **General Summary**
   - Total feeding volume over recent days
   - Volume broken down by type (e.g., breast milk vs. formula)
   - Frequency of feeds per day

2. **Feeding Patterns**
   - Average time between feeds
   - Any consistent feeding times (e.g., every 3–4 hours)
   - Nighttime feedings (feeds between 10:00 PM and 6:00 AM)

3. **Recent Feed Snapshot**
   - Show the last 3–5 feeds with time, milk type, and amount

4. **Insights & Recommendations**
   - Identify any trends (e.g., very frequent or irregular feeds)
   - Suggest simple, actionable advice (e.g., “Try offering a slightly larger feed before bedtime”)
   - Be positive and encouraging — never alarm the reader

5. **Friendly Closing**
   - Always end with a gentle, reassuring sentence (e.g., “You’re doing a wonderful job — keep it up!”)

---

### 💡 Tone & Style:
- Use warm, caring, non-technical language
- Write as if you're a trusted nanny, pediatric nurse, or parenting coach
- Avoid medical or statistical jargon entirely
- Keep the focus on support, encouragement, and practical advice
- **Do NOT output JSON** — this should be a human-friendly text report

---

### ✅ Example Paragraph:

> "Over the past two days, your baby has been feeding about every 3 hours and taking in around 750ml per day, with a nice balance between formula and breast milk. There were two nighttime feedings, which is quite normal at this stage. If you're hoping to reduce night wakings, consider offering a slightly larger feed before bedtime to help your baby sleep longer. You're doing a great job keeping things consistent — keep up the great work!"

Your goal is to turn structured data into a warm, supportive, and insight-rich story for parents, giving them confidence and a few gentle tips to consider.
"""
,
    tools=[analyze_feed_data]
)
