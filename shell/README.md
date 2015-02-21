Makes available in Odoo 8 the `shell` server command available for Odoo 9.

To have this feature available this module just need to be in the
addons path. To use it, in a terminal window run:

    $ ./odoo.py shell -d <dbname>

This will initialize a server instance and then jump into a Pyhton
interactive shell, with full access to the Odoo API.

Example session:

    >>> self
    res.users(1,)
    >>> self.name
    u'Administrator'
    >>> self._name
    'res.users'
    >>> self.env
    <openerp.api.Environment object at 0xb3f4f52c>
    >>> self.env['res.partner'].search([('name', 'like', 'Ag')])
    res.partner(7, 51)
