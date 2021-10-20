# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from urllib.error import URLError

import odoorpc

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class UpgradeComparisonConfig(models.Model):
    _name = "upgrade.comparison.config"
    _description = "Upgrade Comparison Configuration"

    name = fields.Char()

    server = fields.Char(required=True, default="localhost")

    port = fields.Integer(required=True, default=8069)

    database = fields.Char(required=True)

    username = fields.Char(required=True, default="admin")

    password = fields.Char(required=True, default="admin")

    version = fields.Char()

    analysis_ids = fields.One2many(
        string="Analyses", comodel_name="upgrade.analysis", inverse_name="config_id"
    )
    analysis_qty = fields.Integer(compute="_compute_analysis_qty")

    @api.depends("analysis_ids")
    def _compute_analysis_qty(self):
        for config in self:
            config.analysis_qty = len(config.analysis_ids)

    def get_connection(self):
        self.ensure_one()
        try:
            remote = odoorpc.ODOO(self.server, port=self.port)
        except URLError as exc:
            raise UserError(
                _("Could not connect the Odoo server at %(server)s:%(port)s")
                % {"server": self.server, "port": self.port}
            ) from exc
        remote.login(self.database, self.username, self.password)
        self.version = remote.version
        return remote

    def test_connection(self):
        self.ensure_one()
        try:
            connection = self.get_connection()
            user_model = connection.env["res.users"]
            ids = user_model.search([("login", "=", "admin")])
            user_info = user_model.read([ids[0]], ["name"])[0]
        except Exception as e:
            raise UserError(_("Connection failed.\n\nDETAIL: %s") % e) from e
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": "info",
                "message": _(
                    "You are correctly connected to the server %(server)s"
                    " (version %(version)s) with the user %(user_name)s"
                )
                % dict(
                    server=self.server,
                    version=self.version,
                    user_name=user_info["name"],
                ),
            },
        }

    def new_analysis(self):
        self.ensure_one()
        analysis = self.env["upgrade.analysis"].create({"config_id": self.id})
        return {
            "name": analysis._description,
            "view_mode": "form",
            "res_model": analysis._name,
            "type": "ir.actions.act_window",
            # "target": "new",
            "res_id": analysis.id,
            # "nodestroy": True,
        }

    def action_show_analysis(self):
        self.ensure_one()
        return {}
