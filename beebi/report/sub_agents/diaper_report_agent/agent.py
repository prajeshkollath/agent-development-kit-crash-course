from typing import Optional
from google.adk.agents import Agent

# 导入各分析子模块
from beebi.diaper.sub_agents.diaperfrequencyagent.agent import analyze_diaper_frequency
from beebi.diaper.sub_agents.diapertypeanalysisagent.agent import analyze_diaper_type
from beebi.diaper.sub_agents.diapertimingagent.agent import analyze_diaper_timing
from beebi.diaper.sub_agents.diaperdurationagent.agent import analyze_diaper_duration
from beebi.diaper.sub_agents.diaperalertagent.agent import analyze_diaper_alert

# 结构化报告函数
def format_diaper_report(
    days: int,
    frequency_data: dict,
    type_data: dict,
    timing_data: dict,
    duration_data: dict,
    alert_data: dict
) -> str:
    """
    生成结构化尿布分析报告。
    """
    report_lines = [f"Diaper Report for the Last {days} Days\n"]

    # 1. Diaper Change Frequency
    report_lines.append("1. Diaper Change Frequency:")
    avg_per_day = frequency_data.get("avg_per_day", [])
    if avg_per_day:
        for item in avg_per_day:
            if "CustomerID" in item:
                report_lines.append(f"- User {item['CustomerID']}: {item['AvgChangePerDay']:.1f} times/day")
            else:
                report_lines.append(f"- Average: {item['AvgChangePerDay']:.1f} times/day")
    report_lines.append(f"- Frequency summary: {frequency_data.get('summary', '')}\n")

    # 2. Diaper Content Type
    report_lines.append("2. Diaper Content Type:")
    pee_stats = type_data.get("pee_stats", {})
    poo_stats = type_data.get("poo_stats", {})
    report_lines.append(f"- Pee: {pee_stats}")
    report_lines.append(f"- Poo: {poo_stats}")
    report_lines.append(f"- Type summary: {type_data.get('summary', '')}\n")

    # 3. Time of Day Distribution
    report_lines.append("3. Time of Day Distribution:")
    timing_distribution = timing_data.get("timing_distribution", {})
    for period, count in timing_distribution.items():
        report_lines.append(f"- {period}: {count} changes")
    report_lines.append(f"- Timing summary: {timing_data.get('summary', '')}\n")

    # 4. Diaper Change Interval
    report_lines.append("4. Diaper Change Interval:")
    interval_stats = duration_data.get("interval_stats", [])
    if interval_stats:
        for item in interval_stats:
            if "CustomerID" in item:
                report_lines.append(
                    f"- User {item['CustomerID']}: avg {item['avg_interval_hours']}h, min {item['min_interval_hours']}h, max {item['max_interval_hours']}h, count {item['count']}"
                )
            else:
                report_lines.append(
                    f"- Average: {item['avg_interval_hours']}h, min {item['min_interval_hours']}h, max {item['max_interval_hours']}h, count {item['count']}"
                )
    report_lines.append(f"- Interval summary: {duration_data.get('summary', '')}\n")

    # 5. Alerts
    report_lines.append("5. Alerts:")
    alerts = alert_data.get("alerts", [])
    if alerts:
        for alert in alerts:
            report_lines.append(f"- {alert}")
    else:
        report_lines.append("- No abnormal patterns detected.")
    report_lines.append(f"- Alert summary: {alert_data.get('summary', '')}\n")

    # 6. Suggestions
    report_lines.append("6. Suggestions:")
    suggestions = [
        frequency_data.get("recommendation", ""),
        type_data.get("recommendation", ""),
        timing_data.get("recommendation", ""),
        duration_data.get("recommendation", ""),
        alert_data.get("recommendation", "")
    ]
    for rec in suggestions:
        if rec:
            report_lines.append(f"- {rec}")

    return "\n".join(report_lines)


# Agent instruction prompt
instruction_text = """
You are a professional diaper analysis agent. When a user requests a diaper report for the last N days, your task is to generate a data-driven, easy-to-understand, and actionable diaper report.

You must strictly follow this workflow:

1. Call `analyze_diaper_frequency(days=N)` to gather general metrics: average changes per day, by user if needed.
2. Call `analyze_diaper_type(days=N)` to analyze the type and amount of pee/poo.
3. Call `analyze_diaper_timing(days=N)` to analyze the distribution of changes across different times of day.
4. Call `analyze_diaper_duration(days=N)` to analyze the average, min, and max intervals between changes.
5. Call `analyze_diaper_alert(days=N)` to detect abnormal patterns (e.g., consecutive big poos, long intervals).
6. Use the outputs from the above five functions to generate a structured diaper report by calling:
   `format_diaper_report(days=N, frequency, type, timing, duration, alert)`
7. Use the returned structured report to write a **professional but parent-friendly summary**, including the following parts:
   - Diaper Change Frequency: how often, by user if needed
   - Diaper Content Type: pee/poo, and their levels
   - Time of Day Distribution: when changes are most frequent
   - Change Interval: regularity and gaps
   - Alerts: abnormal patterns
   - Suggestions

### SUGGESTIONS

Your suggestions **must** follow these principles:

- Be directly based on the actual diaper data and patterns detected
- Include both:
  - WHY the issue matters (explain consequences clearly, in plain language)
  - WHAT the caregiver can actually do (clear, realistic, and simple steps)
- Avoid using technical jargon or vague advice (e.g., don’t say “improve change routine” — explain what actions that actually involves)

For example:

**❌ Bad:**
- "Improve change regularity."

**✅ Good:**
- "Diaper changes are highly irregular. This may increase the risk of rashes or discomfort. Try to check and change diapers at consistent intervals, such as every 3–4 hours during the day."

Return the final structured report in a format that can be rendered directly by a UI component or formatted for display to parents.

Always prioritize clarity, evidence-based insights, and actionable advice.
"""

# 定义sub-agent
diaper_report_agent = Agent(
    name="diaper_report_agent",
    model="gemini-2.0-flash",
    description="Agent to generate structured diaper report based on 5 analysis functions",
    instruction=instruction_text,
    tools=[
        analyze_diaper_frequency,
        analyze_diaper_type,
        analyze_diaper_timing,
        analyze_diaper_duration,
        analyze_diaper_alert,
        format_diaper_report
    ],
    output_key="diaper_report"
)