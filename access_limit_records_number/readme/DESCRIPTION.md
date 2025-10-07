With this module you can limit number of records for any model in
specified domain. For example, you can restrict number of vehicles in
fleet_vehicle, say by three. If users try to create more then three
vehicles then exception occurs.

This module uses base.action.rule to restrict number of records. And
also there is new model base.limit.records_number to store the settings.

To do new settings to restrict number of records in any model the user
should be a member of `Control limits on records number` security group.

This project is based on this other project:
<https://apps.odoo.com/apps/modules/11.0/access_limit_records_number/>
