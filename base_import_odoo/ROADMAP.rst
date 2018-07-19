* Yes of course this duplicates a lot of connector functionality. Rewrite this with the connector framework, probably collaborate with https://github.com/OCA/connector-odoo2odoo
* Do something with workflows
* Support reference fields, while being at it refactor _run_import_map_values to call a function per field type
* Probably it's safer and faster to disable recomputation during import, and recompute all fields afterwards
* Add duplicate handling strategy 'Overwrite older'
