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
        # Connect to server
        folder_server_object = self.server_id.connect()
        folder_server_object.connect()
        # cd into path
        folder_server_object.cd(self.path)
        return folder_server_object
