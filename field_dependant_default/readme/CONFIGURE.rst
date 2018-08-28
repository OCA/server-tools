Fields must be defined with the function. For example::

        from odoo import api, fields, models


        class ResPartner(models.Model):
            _inherit = 'res.partner'

            ref = fields.Char(dependant_default='default_ref')

            def default_ref(self, vals):
                # Return the exepcted result from your vals
                return 'AAA'
