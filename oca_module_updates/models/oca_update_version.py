# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class OcaUpdateVersion(models.Model):

    _name = "oca.update.version"
    _description = "Oca Update Version"  # TODO

    name = fields.Char(required=True)
    old_system = fields.Boolean()

    _sql_constraints = [
        ("name_uniq", "unique (name)", "The name of the version must be unique!")
    ]

    @api.model_create_multi
    def create(self, list_vals):
        new_vals = []
        to_add = self.browse()
        for vals in list_vals:
            if vals.get("name"):
                version = self.search([("name", "=", vals["name"])])
                if version:
                    to_add |= version
                    continue
            new_vals.append(vals)
        return to_add | super(OcaUpdateVersion, self).create(new_vals)
