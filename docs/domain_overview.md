# Domain Overview — Solar Farm Operations

This document gives the domain context the SolarOps AI platform reasons about.
It is written for engineers who are new to solar generation but need enough
mental model to understand why the agents make the decisions they do.

## 1. What a solar farm produces

A utility-scale solar farm converts incident solar irradiance into electrical
energy. Instantaneous power, and therefore energy over an interval, is driven by
a small set of physical variables:

| Variable | Effect on generation |
| --- | --- |
| **Irradiance (W/m²)** | Primary driver — output scales roughly linearly with plane-of-array irradiance. |
| **Cloud cover (%)** | Attenuates irradiance; heavy cover can cut output by 60–90%. |
| **Panel/ambient temperature (°C)** | Above ~25 °C, cell efficiency drops ~0.4%/°C (temperature derating). |
| **Soiling / shading** | Dust, snow, or obstructions reduce the effective collecting area. |
| **Inverter health** | Converts DC→AC; a degraded or failed inverter/string caps real output. |

The platform models a **weather-adjusted expected generation**: given the
observed weather, a healthy farm of a known capacity *should* produce a
predictable amount of energy. Deviations from that expectation are the signal
the system is built to detect and explain.

## 2. The performance-ratio mental model

Operators monitor the **performance ratio (PR)** — actual output divided by
weather-expected output. A healthy farm sits near PR ≈ 1.0 (minus small,
expected losses and noise). A sustained drop in PR during production hours is
the canonical symptom of a problem:

```
deviation = (expected_kWh - actual_kWh) / expected_kWh
```

SolarOps evaluates this at the **daytime peak-generation hour**, because at night
both expected and actual output are ~0 and the ratio carries no information.

## 3. Why this is an AI / agentic problem

Detecting a number drop is easy; operating a fleet is not. The hard parts are:

- **Forecasting** future generation for grid commitments and curtailment.
- **Separating** weather-driven dips (normal) from equipment faults (actionable).
- **Explaining** the most likely root cause in operational language.
- **Grounding** maintenance guidance in approved procedures, not guesswork.
- **Gating** any costly or risky action behind a human approval.

Each concern maps to a dedicated agent (see `agent_design.md`), coordinated by a
LangGraph orchestrator that carries a single typed state object between nodes.

## 4. Farms in the reference dataset

The reference registry (`configs/app_config.yaml`) defines a small fleet used
for demos and tests. The synthetic data engine generates deterministic,
physics-lite weather and SCADA telemetry per farm so every component runs
offline and reproducibly, with no external API keys required.
