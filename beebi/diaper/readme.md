DiaperFrequencyAgent	统计尿布更换的频率（如每日、每时段、按用户）
DiaperTypeAnalysisAgent	分析尿布内容类型：是否有尿、有便便，分别是small / medium / big
DiaperTimingAgent	分析一天中更换的时间分布（如是否集中在某几个时间段、是否规律）
DiaperDurationAgent	计算每次尿布持续的时间（StartTime ~ 下一次 StartTime）用于分析平均间隔（如果适用）
DiaperAlertAgent	识别不正常的排泄频率或类型，如连续多次 big poo，超过时间未换等（可用于家长提醒系统）