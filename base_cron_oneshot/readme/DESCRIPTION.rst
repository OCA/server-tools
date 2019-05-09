This module extends the functionality of Odoo crons
to allow you to create single-purpose crons without any further setup or modules
such as `queue_job`.

The typical use case is: you have an expensive task to run on demand and only once.

A main cron called "Oneshot cron cleanup" will delete already executed crons each day.
You might want to tune it according to your needs.
