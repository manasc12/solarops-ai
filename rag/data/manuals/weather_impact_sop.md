# Weather Impact and Thermal Derating SOP

## Irradiance and Cloud Cover
Generation scales approximately with plane-of-array irradiance. Heavy cloud cover
(>70%) can reduce output by more than half. Such reductions are expected and should
NOT be flagged as equipment anomalies when inverter status is OK.

## Thermal Derating
PV modules lose roughly 0.3-0.45% of output per degree Celsius above 25C cell
temperature. On hot, high-irradiance days, panel temperatures can exceed 60C,
producing meaningful derating even under clear skies.

Symptoms: lower-than-nameplate output at high panel temperature; output recovers
as temperatures fall in the evening.

Recommended actions:
1. Confirm panel temperature readings against ambient + irradiance expectations.
2. Ensure adequate module ventilation and clearance.
3. Treat thermal derating as expected behavior, not a fault, unless output is far
   below the temperature-adjusted forecast.

## High Wind
Wind speeds above 15 m/s may trigger tracker stow events, temporarily flattening
panels and reducing output. Verify tracker state before investigating other causes.
