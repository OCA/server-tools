If you install the module, you will find a tab on the company form allowing
to define the technical user.

In your code you can use the following helper that will return you

- a self with the user tech if configured
- or a self with sudo user

.. code-block:: python

    self_tech = self.sudo_tech()

If you want to raise an error if the tech user in not configured just call it with

.. code-block:: python

    self_tech = self.sudo_tech(raise_if_missing)
