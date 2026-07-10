This module lets you restrict a scheduled action (cron) from running on
specific weekdays.

Every scheduled action gains a set of per-weekday checkboxes (all
enabled by default, so behaviour is unchanged until you deselect a day).
When a run would fall on a deselected weekday, it is deferred to the
next allowed day at the same time of day instead of executing.

A common use case is skipping heavy or external-integration jobs on
weekends, when the remote service publishes nothing and the run has
nothing to do.
