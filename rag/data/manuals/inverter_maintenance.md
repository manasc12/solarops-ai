# Inverter Maintenance Manual

## Overview
String and central inverters convert DC from PV panels to grid-synchronized AC.
Inverter faults are the most common cause of sudden generation loss at a solar farm.

## Fault: Inverter Failure (status FAILURE)
Symptoms: zero or near-zero AC output from an inverter while irradiance is adequate;
fault LED illuminated; communication watchdog timeout.
Likely causes:
- IGBT/power-stage failure
- DC isolation fault tripping protection
- Grid over/under-voltage lockout

Recommended actions:
1. Verify DC input voltage at the combiner box.
2. Inspect for ground/isolation faults before re-energizing.
3. If the power stage is faulted, raise a work order to replace the inverter module.
4. Do not reset more than twice; repeated trips indicate hardware damage.

## Fault: Inverter Degraded (status DEGRADED)
Symptoms: output 30-60% below expected for the given irradiance; elevated internal
temperature; intermittent string dropouts.
Likely causes:
- Partial string disconnection or blown string fuse
- Cooling fan failure causing thermal derating
- MPPT tracking error on one channel

Recommended actions:
1. Check string-level currents for imbalance.
2. Replace blown string fuses and reseat MPPT connectors.
3. Clean or replace cooling fans; verify ambient ventilation.

## Preventive Maintenance
- Inspect torque on DC/AC terminations quarterly.
- Clean heat sinks and verify fan operation before peak season.
- Review event logs weekly for recurring warning codes.
