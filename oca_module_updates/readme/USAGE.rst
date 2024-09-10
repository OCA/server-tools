- Access the menu `OCA Updates`
- Create a new module. You should set the version of the module
- You can refresh the data manually pressing the button `Refresh`
- Otherwise, you can wait for the cron job to refresh the data

It is important to notice that the cron job just does a 100 modules on each refresh.
If you have a lot of modules, you should change the cron job to run more often.
