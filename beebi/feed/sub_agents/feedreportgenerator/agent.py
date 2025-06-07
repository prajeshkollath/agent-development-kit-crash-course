from typing import Optional
from google.adk.agents import Agent

# 导入各分析子模块
from ..feedconsistencyagent.agent import analyze_feed_consistency
from ..feedintervalagent.agent import analyze_feed_intervals
from ..feedtimeofdayagent.agent import analyze_feed_time_of_day
from ..feedtypeagent.agent import analyze_feed_type_ratio
from ..feedvolumeagent.agent import analyze_feed_volume

# 结构化报告函数
def format_feed_report(
    days: int,
    consistency_data: dict,
    interval_data: dict,
    timeofday_data: dict,
    type_data: dict,
    volume_data: dict
) -> str:
    """
    生成结构化英文喂奶报告。
    """
    report_lines = [f"Feeding Report for the Last {days} Days\n"]

    # 1. Feeding Volume Overview
    report_lines.append("1. Feeding Volume Overview:")
    report_lines.append(f"- Total volume: {volume_data.get('total_volume_ml', 'N/A')} ml")
    report_lines.append(f"- Average per feed: {volume_data.get('average_volume_per_feed', 'N/A')} ml")
    report_lines.append(f"- Feeds per day: {volume_data.get('feeds_per_day', 'N/A')}\n")

    # 2. Feeding Type Ratio
    report_lines.append("2. Feeding Type Ratio:")
    report_lines.append(f"- Breast milk ratio: {type_data.get('breast_milk_ratio', 'N/A')}")
    report_lines.append(f"- Formula milk ratio: {type_data.get('formula_milk_ratio', 'N/A')}")
    report_lines.append(f"- Type summary: {type_data.get('summary', '')}\n")

    # 3. Time of Day Distribution
    report_lines.append("3. Time of Day Distribution:")
    peak_periods = timeofday_data.get("peak_periods", {})
    for period, count in peak_periods.items():
        report_lines.append(f"- {period}: {count} feeds")
    report_lines.append(f"- Time summary: {timeofday_data.get('summary', '')}\n")

    # 4. Feeding Interval Consistency
    report_lines.append("4. Feeding Interval Consistency:")
    report_lines.append(f"- Average interval: {interval_data.get('average_interval_hours', 'N/A')} hours")
    report_lines.append(f"- Min interval: {interval_data.get('min_interval_hours', 'N/A')} hours")
    report_lines.append(f"- Max interval: {interval_data.get('max_interval_hours', 'N/A')} hours")
    report_lines.append(f"- Std deviation: {interval_data.get('std_dev_hours', 'N/A')}")
    report_lines.append(f"- Interval summary: {interval_data.get('summary', '')}\n")

    # 5. Feed Consistency (Volume & Timing)
    report_lines.append("5. Feed Consistency (Volume & Timing):")
    report_lines.append(f"- Time variability (CV): {consistency_data.get('time_variability_cv', 'N/A')}")
    report_lines.append(f"- Volume variability (CV): {consistency_data.get('volume_variability_cv', 'N/A')}")
    report_lines.append(f"- Time pattern: {consistency_data.get('time_pattern', '')}")
    report_lines.append(f"- Volume pattern: {consistency_data.get('volume_pattern', '')}\n")

    # 6. Suggestions
    report_lines.append("6. Expert Suggestions:")
    # 汇总所有建议
    suggestions = [
        volume_data.get("recommendation", ""),
        type_data.get("recommendation", ""),
        timeofday_data.get("recommendation", ""),
        interval_data.get("recommendation", ""),
        consistency_data.get("recommendation", "")
    ]
    for rec in suggestions:
        if rec:
            report_lines.append(f"- {rec}")

    return "\n".join(report_lines)


# Agent instruction prompt
instruction_text = """
You are a professional baby feeding analyst agent. When a user requests a feeding report for the last N days, your task is to generate a data-driven, easy-to-understand, and actionable feeding report.

You must strictly follow this workflow:

1. Call `analyze_feed_volume(days=N)` to gather general metrics: total volume, average per feed, feeds per day, etc.
2. Call `analyze_feed_type_ratio(days=N)` to analyze the ratio and trend of breast milk vs formula.
3. Call `analyze_feed_time_of_day(days=N)` to analyze feeding distribution across different times of day.
4. Call `analyze_feed_intervals(days=N)` to analyze the regularity and intervals between feeds.
5. Call `analyze_feed_consistency(days=N)` to analyze the variability and consistency of feeding times and volumes.
6. Use the outputs from the above five functions to generate a structured feeding report by calling:
   `format_feed_report(days=N, consistency, interval, timeofday, type, volume)`
7. Use the returned structured report to write a **professional but parent-friendly summary**, including the following parts:
   - Feeding Volume Overview: total, average, frequency
   - Feeding Type Ratio: breast milk vs formula
   - Time of Day Distribution: when feeding is most frequent
   - Interval Consistency: regularity of feeding intervals
   - Consistency: variability in timing and volume
   - Suggestions

### SUGGESTIONS

Your suggestions **must** follow these principles:

- Be directly based on the actual feeding data and patterns detected
- Include both:
  - WHY the issue matters (explain consequences clearly, in plain English)
  - WHAT the caregiver can actually do (clear, realistic, and simple steps)
- Avoid using technical jargon or vague advice (e.g., don’t say “improve feeding routine” — explain what actions that actually involves)

For example:

**❌ Bad:**
- "Improve feeding regularity."

**✅ Good:**
- "Feeding intervals are highly irregular. This may make your baby fussy or hungry at unpredictable times. Try to keep feeding times within a 1–2 hour window each day for better predictability."

Return the final structured report in a format that can be rendered directly by a UI component or formatted for display to parents.

Always prioritize clarity, evidence-based insights, and actionable advice.
"""

# 定义sub-agent
feed_report_generator = Agent(
    name="feed_report_generator",
    model="gemini-2.0-flash",
    description="Agent to generate structured feeding report based on 5 analysis functions",
    instruction=instruction_text,
    tools=[
        analyze_feed_volume,
        analyze_feed_type_ratio,
        analyze_feed_time_of_day,
        analyze_feed_intervals,
        analyze_feed_consistency,
        format_feed_report
    ],
)