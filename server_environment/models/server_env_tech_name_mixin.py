# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp (http://www.camptocamp.com)
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..tools import slugify


class ServerEnvTechNameMixin(models.AbstractModel):
    """Provides a tech_name field to be used in server env vars as unique key.

    The `name` field can be error prone because users can easily change it
    to something more meaningful for them or set weird chars into it
    that make difficult to reference the record in env var config.
    This mixin helps solve the problem by providing a tech name field
    and a cleanup machinery as well as a unique constrain.

    To use this mixin add it to the _inherit attr of your module like:

        _inherit = [
            "my.model",
            "server.env.techname.mixin",
            "server.env.mixin",
        ]

    """

    _name = "server.env.techname.mixin"
    _description = "Server environment technical name"
    _sql_constraints = [
        ("tech_name_uniq", "unique(tech_name)", "`tech_name` must be unique!",)
    ]
    # TODO: could leverage the new option for computable / writable fields
    # and get rid of some onchange / read / write code.
    tech_name = fields.Char(
        help="Unique name for technical purposes. Eg: server env keys.",
    )

    _server_env_section_name_field = "tech_name"

    @api.onchange("name")
    def _onchange_name_for_tech(self):
        # Keep this specific name for the method to avoid possible overrides
        # of existing `_onchange_name` methods
        if self.name and not self.tech_name:
            self.tech_name = self.name

    @api.onchange("tech_name")
    def _onchange_tech_name(self):
        if self.tech_name:
            # make sure is normalized
            self.tech_name = self._normalize_tech_name(self.tech_name)

    @api.model
    def create(self, vals):
        self._handle_tech_name(vals)
        return super(ServerEnvTechNameMixin, self).create(vals)

    def write(self, vals):
        self._handle_tech_name(vals)
        return super(ServerEnvTechNameMixin, self).write(vals)

    def _handle_tech_name(self, vals):
        # make sure technical names are always there
        if not vals.get("tech_name") and vals.get("name"):
            vals["tech_name"] = self._normalize_tech_name(vals["name"])

    @staticmethod
    def _normalize_tech_name(name):
        return slugify(name).replace("-", "_")
