"""Prompt templates for the Root Cause Analysis Agent."""

RCA_SYSTEM = (
    "You are a senior solar operations reliability engineer. Given structured "
    "telemetry, weather context, and ranked candidate causes, write a concise, "
    "grounded root-cause explanation. Do not invent causes beyond those provided."
)

RCA_PROMPT_TEMPLATE = """Farm: {farm_id}
Anomaly score: {anomaly_score} (severity {severity})
Forecast vs actual deviation: {deviation_pct}%
Inverter status: {inverter_status}
Weather: cloud {cloud_cover_pct}%, irradiance {irradiance_wm2} W/m2, panel temp {panel_temperature_c}C

Candidate causes (ranked): {causes}

Explain the most likely root cause(s) in 2-3 sentences, grounded only in the data above.
"""
