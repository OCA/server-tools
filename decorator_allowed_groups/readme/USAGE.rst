Once installed, the following code:

.. code-block:: xml

    <button type="object" name="my_action" groups="purchase.group_purchase_manager"/>

.. code-block:: python

    def my_action(self):
        if not self.env.user.has_group("purchase.group_purchase_manager"):
            raise AccessError(_("Some Error"))
        pass

can be replaced by:

.. code-block:: xml

    <button type="object" name="my_action"/>

.. code-block:: python

    @api.allowed_groups("purchase.group_purchase_manager")
    def my_action(self):
        pass


Multi-group membership checks
-----------------------------

It is possible to list many groups. In that case, the action will be allowed
if the user belong to at least one group.

.. code-block:: python

    @api.allowed_groups("purchase.group_purchase_manager", "sale.group_sale_manager")
    def my_action(self):
        pass


Conflict between view and decorators definition
-----------------------------------------------

The groups defined in the decorators take precedence over the groups that would be defined in the existing views.


Inheritance mechanisms
----------------------

it is possible to change accreditation level in custom module.

For exemple, if a module A defines a function like this:

.. code-block:: python

    @api.allowed_groups("purchase.group_purchase_manager")
    def my_action(self):
        pass

In a custom module B, that depends on module A :

* You can overwrite accreditation level by writing

.. code-block:: python

    # Now checks if user is member of 'purchase.group_purchase_user'
    @api.allowed_groups("purchase.group_purchase_user")
    def my_action(self):
        return super().my_action()

* You can remove checkes, by writing

.. code-block:: python

    # No longer performs checks
    @api.allowed_groups()
    def my_action(self):
        return super().my_action()

* You can only overload the function, without changing the accreditation level by writing

.. code-block:: python

    # the user must always be a member of 'purchase.group_purchase_manager'
    def my_action(self):
        # Custom code ...
        return super().my_action()
