1.  Go to *Settings \> Technical \> Automation \> Scheduled Actions*
    (developer mode).
2.  Open a scheduled action.
3.  Under *Run on Weekdays*, deselect the days on which the action must
    not run.
4.  Save. At least one weekday must stay selected.

Notes:

- The weekday is evaluated in the timezone of the action's *Scheduler
  User*.
- Only the scheduled cadence is affected. Running an action manually or
  through a code trigger still executes it regardless of the selected
  weekdays.
