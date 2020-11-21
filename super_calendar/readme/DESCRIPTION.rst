This module allows to create configurable calendars.

Through the 'calendar configurator' object, you can specify which models have
to be merged in the super calendar. For each model, you have to define the
'description' and 'date_start' fields at least. Then you can define 'duration'
and the 'user_id' fields.

The 'super.calendar' object contains the merged calendars. The
'super.calendar' can be updated by 'ir.cron' or manually.
