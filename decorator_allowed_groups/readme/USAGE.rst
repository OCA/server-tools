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


Note
----

- it is possible to list many groups. In that case, the action will be allowed
  if the user belong to at least one group.

.. code-block:: python

    @api.allowed_groups("purchase.group_purchase_manager", "sale.group_sale_manager")
    def my_action(self):
        pass

- it is possible to change accreditation level in custom module.

For exemple, if a module define a function like this:

.. code-block:: python

    @api.allowed_groups("purchase.group_purchase_manager")
    def my_action(self):
        pass

Another module that depends on the first module can redefine the accreditation
level by writing.

.. code-block:: python

    @api.allowed_groups("purchase.group_purchase_user")
    def my_action(self):
        return super().my_action()
