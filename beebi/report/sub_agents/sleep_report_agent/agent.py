from typing import Optional
from google.adk.agents import Agent


# 结构化报告函数
def format_sleep_report(
    days: int,
    sessions_data: dict,
    anomalies_data: dict,
    patterns_data: dict
) -> str:
    """
    根据三个分析函数结果，生成结构化英文睡眠报告。
    参数:
    - days: 分析的天数
    - sessions_data: analyze_sleep_sessions 返回结果
    - anomalies_data: detect_sleep_anomalies 返回结果
    - patterns_data: analyze_sleep_patterns 返回结果
    
    返回:
    - 一段格式化的英文报告文本
    """
    
    report_lines = [f"Sleep Report for the Last {days} Days\n"]
    
    # 1. Overview
    overview = sessions_data.get("summary", {})
    report_lines.append("1. Overview:")
    report_lines.append(f"- Total days analyzed: {overview.get('days_analyzed', 'N/A')}")
    report_lines.append(f"- Total sleep sessions: {overview.get('total_sessions', 'N/A')}")
    report_lines.append(f"- Average sleep duration per day: {overview.get('avg_hours_per_day', 'N/A')} hours")
    report_lines.append(f"- Average duration per sleep session: {overview.get('avg_duration_per_session_minutes', 'N/A')} minutes\n")
    
    # 2. Sleep Quality Distribution
    quality = overview.get("sleep_quality_distribution", {})
    report_lines.append("2. Sleep Quality Distribution:")
    report_lines.append(f"- Poor quality sleeps: {quality.get('Poor', 0)}")
    report_lines.append(f"- Good quality sleeps: {quality.get('Good', 0)}")
    report_lines.append(f"- Rich quality sleeps: {quality.get('Rich', 0)}\n")
    
    # 3. Sleep Timing Distribution
    timing = patterns_data.get("timing_distribution", {})
    report_lines.append("3. Sleep Timing Distribution:")
    report_lines.append(f"- Morning (6 AM - 12 PM): {timing.get('morning', 0)} sessions")
    report_lines.append(f"- Afternoon (12 PM - 6 PM): {timing.get('afternoon', 0)} sessions")
    report_lines.append(f"- Evening (6 PM - 12 AM): {timing.get('evening', 0)} sessions")
    report_lines.append(f"- Night (12 AM - 6 AM): {timing.get('night', 0)} sessions\n")
    
    # 4. Sleep Regularity
    regularity = patterns_data.get("regularity", {})
    report_lines.append("4. Sleep Regularity:")
    report_lines.append(f"- Average sleep onset variability (hours): {regularity.get('onset_variability', 'N/A')}")
    report_lines.append(f"- Std deviation of sleep duration (minutes): {regularity.get('duration_std', 'N/A')}")
    report_lines.append(f"- Description: {regularity.get('description', 'N/A')}\n")
    
    # 5. Anomaly Detection
    anomalies = anomalies_data.get("summary", {})
    report_lines.append("5. Anomaly Detection:")
    report_lines.append(f"- Very short sleeps (<3h): {anomalies.get('short_sleeps', 0)}")
    report_lines.append(f"- Very long sleeps (>10h): {anomalies.get('long_sleeps', 0)}")
    report_lines.append(f"- Short interval sleeps (<4h): {anomalies.get('short_intervals', 0)}\n")
    
    # 6. Suggestions
    report_lines.append("6. Expert Suggestions:")
    
    return "\n".join(report_lines)


from beebi.sleep.sub_agent.sleep_analysis_agent.agent import analyze_sleep_sessions
from beebi.sleep.sub_agent.sleep_anomaly_detector.agent import detect_sleep_anomalies
from beebi.sleep.sub_agent.sleep_pattern_agent.agent import analyze_sleep_patterns

# Agent instruction prompt
instruction_text = """
You are a professional baby sleep analyst agent. When a user requests a sleep report for the last N days, your task is to generate a data-driven, easy-to-understand, and actionable sleep report.

You must strictly follow this workflow:

1. Call `analyze_sleep_sessions(days=N)` to gather general metrics: total sleep time, average duration, sleep efficiency, etc.
2. Call `detect_sleep_anomalies(days=N)` to identify unusual events such as missed naps or frequent night wakings.
3. Call `analyze_sleep_patterns(days=N)` to detect recurring patterns: nap timing, bedtime consistency, and regularity of sleep sessions.
4. Use the outputs from the above three functions to generate a structured sleep report by calling:
   `format_sleep_report(days=N, sessions, anomalies, patterns)`
5. Use the returned structured report to write a **professional but parent-friendly summary**, including the following parts:
   - Sleep Overview: total hours, quality, number of sessions
   - Sleep Timing Distribution: nap/overnight sleep breakdown
   - Regularity Analysis: consistency in onset time and duration
   - Anomalies: missed naps, fragmented sleep, irregular sleep
   - Suggestions

### SUGGESTIONS

Your suggestions **must** follow these principles:

- Be directly based on the actual sleep data and anomalies detected
- Include both:
  - WHY the issue matters (explain consequences clearly, in plain English)
  - WHAT the caregiver can actually do (clear, realistic, and simple steps)
- Avoid using technical jargon or vague advice (e.g., don’t say “improve sleep hygiene” — explain what actions that actually involves)

For example:

**❌ Bad:**
- "Improve sleep quality by adjusting bedtime routines."

**✅ Good:**
- "Your child wakes up 2–3 times every night. This may be due to an inconsistent bedtime. Try putting your child to bed at the same time each night and use a calming routine (bath, story, cuddle) 30 minutes before bedtime."

Return the final structured report in a format that can be rendered directly by a UI component or formatted for display to parents.

Always prioritize clarity, evidence-based insights, and actionable advice.
"""


# 定义sub-agent
sleep_report_agent = Agent(
    name="sleep_report_agent",
    model="gemini-2.0-flash",
    description="Agent to generate structured sleep report based on 3 analysis functions",
    instruction=instruction_text,
    tools=[
        analyze_sleep_sessions,
        detect_sleep_anomalies,
        analyze_sleep_patterns,
        format_sleep_report
    ],
    output_key="sleep_report"
)
