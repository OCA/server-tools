This module adjust cron to run at fixed hours, local time.


Without this module, when a daylight saving time change occur, the cron will not take
the hour change in account.

With this module, when a daylight saving time change occur, the offset (+1 or -1 hour)
will be applied.
