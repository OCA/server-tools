To configure this module, you need to:

1. Go to Settings/Technical/Automation/Scheduled Actions
2. Select actions *Vacuum Postgresql Tables* and *Analyze Postgresql Tables*
3. Adapt the schedule to run at a time when your Odoo installation is least busy, take care that the analyze and vacuum cronjobs won't run simultaneously
4. Adapt the parameters to match your setting, but the defaults should be fine for most users
5. Note that the vacuum cronjob is inactive by default, because this is a potentially very heavy operation
