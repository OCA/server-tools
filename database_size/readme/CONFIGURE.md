To configure this module, you can review the scheduled action called 'Take model
size measurements' and check the time at which you want it to run. It should
only run once a day. If it runs more often, it just updates the existing set of
sizes for the day.

You may also review the Database Size settings in Odoo's general settings and
enable 'Purge Older Model Size Measurements'. This task will by default delete
most daily data older than a year except for the data captured on the first day
of each month. These retention periods can be configured here as well.
