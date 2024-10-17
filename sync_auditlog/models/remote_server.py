# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AuditlogRemoteServer(models.Model):
    _name = "auditlog.remote.server"
    _description = "Auditlog - Remote Server"

    name = fields.Char("Name", required=1)
    url = fields.Char("Server Url", required=1)
    user = fields.Char("User", required=1)
    password = fields.Char("Password", required=1)
    dbname = fields.Char("Database", required=1)
