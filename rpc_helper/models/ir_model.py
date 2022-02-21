# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import json

from odoo import api, fields, models, tools

from odoo.addons.base_sparse_field.models.fields import Serialized


class IrModel(models.Model):
    _inherit = "ir.model"

    rpc_config = Serialized(compute="_compute_rpc_config", default={})
    # Allow editing via UI
    rpc_config_edit = fields.Text(
        help="Configure RPC config via JSON. "
        "Value must be a list of methods to disable "
        "wrapped by a dict with key `disable`. "
        "Eg: {'disable': ['search', 'do_this']}"
        "To disable all methods, use `{'disable: ['all']}`",
        inverse="_inverse_rpc_config_edit",
    )

    @api.depends("rpc_config_edit")
    def _compute_rpc_config(self):
        for rec in self:
            rec.rpc_config = rec._load_rpc_config()

    def _inverse_rpc_config_edit(self):
        for rec in self:
            # Make sure options_edit is always readable
            rec.rpc_config_edit = json.dumps(
                rec.rpc_config or {}, indent=4, sort_keys=True
            )

    def _load_rpc_config(self):
        return json.loads(self.rpc_config_edit or "{}")

    @tools.ormcache("model")
    def _get_rpc_config(self, model):
        rec = self._get(model)
        return rec.rpc_config or {}
