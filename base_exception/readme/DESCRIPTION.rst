This module provides an abstract model(base.exception) to manage customizable
exceptions to be applied on different models (sale order, invoice, crm, ...).

It also provides an abstract model(exception.mixin) to manage exceptions per stage_id.
For example, the crm.stage inherits this model and adds exception rules in the stage to check these rules for this stage.

It is not useful by itself. You can see an example of implementation
in the 'sale_exception' module. (sale-workflow repository) or
'purchase_exception' module (purchase-workflow repository). or 
'crm_exception' module (crm repository).
