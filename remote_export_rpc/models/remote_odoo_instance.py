# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import xmlrpc.client

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class RemoteOdooInstance(models.Model):
    _name = "remote.odoo.instance"
    _description = "Remote Odoo Instance"

    name = fields.Char(required=True)
    url = fields.Char(
        required=True,
        help="Base URL of the remote Odoo (e.g. https://example.odoo.com)",
    )
    database = fields.Char(required=True)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    active = fields.Boolean(default=True)

    def _get_common_proxy(self):
        self.ensure_one()
        return xmlrpc.client.ServerProxy(
            "{}/xmlrpc/2/common".format(self.url.rstrip("/")), allow_none=True
        )

    def _get_object_proxy(self):
        self.ensure_one()
        return xmlrpc.client.ServerProxy(
            "{}/xmlrpc/2/object".format(self.url.rstrip("/")), allow_none=True
        )

    def _authenticate(self):
        self.ensure_one()
        try:
            uid = self._get_common_proxy().authenticate(
                self.database, self.username, self.password, {}
            )
        except Exception as e:
            raise UserError(
                _("Connection error to %(name)s: %(err)s")
                % {"name": self.name, "err": e}
            ) from e
        if not uid:
            raise UserError(_("Authentication failed for instance %s") % self.name)
        return uid

    def execute_kw(self, model, method, args, kwargs=None):
        self.ensure_one()
        uid = self._authenticate()
        return self._get_object_proxy().execute_kw(
            self.database, uid, self.password, model, method, args, kwargs or {}
        )

    def action_test_connection(self):
        for record in self:
            uid = record._authenticate()
            _logger.info("Remote Odoo %s authenticated with uid=%s", record.name, uid)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Connection successful"),
                "type": "success",
                "sticky": False,
            },
        }
