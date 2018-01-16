# -*- coding: utf-8 -*-
# Copyright 2016 - Ursa Information Systems <http://ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def fetch_export_models(self):
        accessobj = self.env['ir.model.access']
        accessobj_ids = accessobj.search([
            ('perm_export', '=', True),
            ('group_id', 'in', self.env.user.groups_id.ids),
        ])
        model_names = [
            access_obj.model_id.model for access_obj in accessobj_ids
            ]
        return list(set(model_names))
