This module provides an abstract model(base.exception) to manage customizable
exceptions to be applied on different models (sale order, invoice, crm, ...).

It also provides an abstract model (exception.mixin) to establish a relationship between an exception and another model.

It is not useful by itself. You can see an example of implementation
in the 'sale_exception' module. (sale-workflow repository) or
'purchase_exception' module (purchase-workflow repository). or
'crm_exception' module (crm repository).

Background
~~~~~~~~~~

The values of fields in Odoo can be set as translatable. When users want to define an exception where the filtering conditions include the value of a translatable field,
the exception will only take effect when users use the same language as defined in the exception rule.
An abstract model (exception.mixin) is provided to address this inconvenience.
For instance, instead of setting some fields as required in certain CRM stages based on the stage name, which is translatable, users can only define field conditions on exceptions.
They can then select these exceptions for specific stages, ensuring that the exceptions function properly in any language used by the users.
