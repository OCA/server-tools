# -*- coding: utf-8 -*-
from openerp import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    maintenance_mode = fields.Boolean(
        string='Maintenance Mode',
        default=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
