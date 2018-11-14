This module provides the basis for creating key performance indicators,
including static and dynamic thresholds (SQL query or Python code),
on local and remote data sources.

The module also provides the mecanism to update KPIs automatically.
A scheduler is executed every hour and updates the KPI values, based
on the periodicity of each KPI. KPI computation can also be done
manually.

A threshold is a list of ranges and a range is:

* a name (like Good, Warning, Bad)
* a minimum value (fixed, sql query or python code)
* a maximum value (fixed, sql query or python code)
* color (RGB code like #00FF00 for green, #FFA500 for orange, #FF0000 for red)