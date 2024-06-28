- On larger databases, it is possible that backups will die due to Odoo
  server settings. In order to circumvent this without frivolously
  changing settings, you need to run the backup from outside of the main
  Odoo instance. How to do this is outlined in [this blog
  post](https://blog.laslabs.com/2016/10/running-python-scripts-within-odoos-environment/).
- Backups won't work if list_db=False is configured in the instance.
