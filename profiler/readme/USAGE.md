To use this module, you need to:

- got to General Settings > Proflier > profiled functions and create a new record with the name of the function you want to profile, and the model if it's a method of a model. For example, if you want to profile the method `my_method` of the model `my.model`, you need to create a record with the name `my_method` and the model `my.model.my_method`.
EG: 
- name: Stock Rule
- Python Path: odoo.addons.stock.models.stock_rule.ProcurementGroup.run_scheduler
- Sample rate (from 0 to 1): 0.1 (to profile 10% of the calls to this method and avoid too much overhead)
- Active if you want it to be active.

