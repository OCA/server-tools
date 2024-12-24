When you want to limit the update permissions of a model to certain groups:

#. Go to *Settings > Techinical > Database Structure > Models*
#. Open the form view of the model, and select **Update Restrict Model**
#. Assign the groups that should be exempt from the restriction to **Update-allowed Groups**


When you want revoke update permissions for a specific user:

#. Go to *Settings > Users & Companies > Users*
#. Open the user's form view and click the **Read-only** smart button
#. In case you wish to exclude some models from being read-only, go to *Settings >
   General Settings* and update **Excluded Models from Read-only** under the Permissions
   section by listing the models separated by commas (e.g., `sale.order,sale.order.line`).
