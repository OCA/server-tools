If you have to decompose a complex domain to inject some conditions,
this shows what you can do:

.. code-block:: python

    from odoo.osv.expression import AND, OR
    from odoo.addons.base_domain_inverse_function.expression import inverse_AND, inverse_OR

    domain = AND([d1, d2, d3])
    d1, d2, d3 = inverse_AND(domain)

    domain = OR([d1, d2, d3])
    d1, d2, d3 = inverse_OR(domain)
