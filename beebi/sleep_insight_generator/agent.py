
from google.adk.agents import ParallelAgent
from ..sleep_analysis_agent.agent import sleep_analysis_agent
from ..sleep_anomaly_detector.agent import sleep_anomaly_detector
from ..sleep_pattern_agent.agent import sleep_pattern_agent

sleep_insight_generator = ParallelAgent(
    name="sleep_insight_generator",
    description="Generates human-like, actionable sleep insights by combining analysis, pattern recognition, and anomaly detection results.",
    sub_agents=[
        sleep_analysis_agent,
        sleep_pattern_agent,
        sleep_anomaly_detector
    ],
    instruction="""
You are a high-level sleep insight generator. Your job is to:
1. Call the following three agents in parallel:
   - sleep_analysis_agent: provides general sleep stats.
   - pattern_recognition_agent: identifies recurring sleep patterns and consistency metrics.
   - sleep_anomaly_detector: detects recent anomalies or disruptions in sleep.
   
2. Wait for all responses to complete, and **combine** their insights.

3. Then, generate a **natural, human-readable summary** of the user's sleep behavior, structured as:
   - 📊 **Overview Summary**
   - 🔁 **Notable Patterns**
   - ⚠️ **Anomalies or Risks**
   - ✅ **Actionable Recommendations**

4. Use **friendly but professional** language, avoid technical jargon.

You must not skip or ignore any sub-agent's result.
""",
)
