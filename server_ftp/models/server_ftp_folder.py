# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ServerFTPFolder(models.Model):
    _name = "server.ftp.folder"
    _description = "Server ftp folder"

    name = fields.Char()
    path = fields.Char(help="change path upon connection")
    server_id = fields.Many2one(comodel_name="server.ftp")

    def connect(self):
        """ Return appropriate FTP class, cd into path"""
        server = self.server_id.connect()
        server.cd(self.path)
        return server
