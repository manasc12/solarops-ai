# Failure Modes — Solar Farm Equipment & Performance

This catalogue describes the failure modes the anomaly and RCA agents reason
about. Each entry lists the operational signature (what the data looks like) and
the typical root cause, so the reasoning layer can map an observed deviation to a
ranked set of explanations.

## 1. Inverter failure

- **Signature:** Sharp, sustained output drop (often 60–90% below expected)
  during otherwise good irradiance. Inverter status reports `FAILURE`. Affected
  string voltage/current collapse.
- **Root cause:** DC/AC converter fault, blown fuse, IGBT failure, or grid
  disconnect on a string.
- **Severity:** HIGH — drives the human-in-the-loop approval path.

## 2. Inverter degradation / partial string underperformance

- **Signature:** Moderate output drop (30–55% below expected). Inverter status
  `DEGRADED`. One string lags its peers under identical weather.
- **Root cause:** Aging components, thermal throttling, or a partially faulted
  string.
- **Severity:** MEDIUM–HIGH depending on magnitude.

## 3. Soiling

- **Signature:** Gradual, persistent reduction in PR (typically 5–20%) that does
  not recover and is uncorrelated with cloud cover.
- **Root cause:** Dust, pollen, bird droppings, or agricultural deposits on the
  panel surface reducing effective irradiance.
- **Severity:** LOW–MEDIUM. Resolved by cleaning, not emergency action.

## 4. Shading

- **Signature:** Time-of-day-correlated dips that recur at the same solar angle;
  partial array affected while the rest performs normally.
- **Root cause:** Vegetation growth, new structures, or soiling on a sub-array.
- **Severity:** LOW–MEDIUM.

## 5. Weather-driven dip (NOT a fault)

- **Signature:** Output drop that tracks cloud cover / low irradiance. Expected
  generation drops with it, so PR stays near 1.0.
- **Root cause:** Cloud transit, storms, seasonal low sun.
- **Severity:** LOW — explicitly classified as normal so it does **not** trigger
  RCA or an approval. Distinguishing this from a real fault is the core value of
  the weather-adjusted baseline.

## 6. Temperature derating

- **Signature:** Mild efficiency loss at high panel temperatures; correlates with
  ambient temperature, recovers as it cools.
- **Root cause:** Physics — cell efficiency falls above ~25 °C.
- **Severity:** LOW. Modeled directly in the expected-generation baseline.

## How the system uses this catalogue

1. The **anomaly agent** computes the weather-adjusted deviation and inverter
   health, then scores it with an IsolationForest to flag outliers.
2. The **RCA agent** maps the anomaly's signature (deviation magnitude, inverter
   status, weather context) to a ranked list of the causes above.
3. The **RAG layer** grounds the recommended remediation in the approved
   maintenance manuals (`rag/data/manuals/`) so guidance is never hallucinated.
