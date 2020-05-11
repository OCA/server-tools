# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, exceptions, fields, models

from ..lib.ftp_server import FTPServer
from ..lib.sftp_server import SFTPServer


class ServerFTP(models.Model):
    _name = "server.ftp"
    _description = "Server FTP"

    name = fields.Char(required=True)
    host = fields.Char(required=True)
    user = fields.Char(required=True, default="anonymous", string="Username")
    password = fields.Char()
    port = fields.Integer(required=True, default=21)
    server_type = fields.Selection(
        selection=[("FTP", "FTP"), ("ftpls", "FTP_TLS"), ("sftp", "SFTP")],
        string="Connection protocol",
        required=True,
    )
    state = fields.Selection(
        selection=[("draft", "Not Confirmed"), ("done", "Confirmed")],
        default="draft",
        readonly=True,
        required=True,
    )
    folder_ids = fields.One2many(
        comodel_name="server.ftp.folder", inverse_name="server_id"
    )

    def write(self, vals):
        self.ensure_one()
        fields = ["name", "user", "password", "port", "host", "server_type"]
        if any([i in vals for i in fields]):
            # Reset state if someone edits a connection field
            vals["state"] = "draft"
        return super(ServerFTP, self).write(vals)

    def action_test_connection(self):
        """ Test the outcome of connect() """
        if not all([self.host, self.user, self.password, self.port]):
            raise exceptions.Warning(_("Make sure that required info is set"))
        try:
            server = self.connect()
            server = server.connect()
        except Exception as e:
            raise exceptions.Warning(str(e))
        else:
            # Check if all folders are accessible
            not_accessible_folders = []
            for folder in self.folder_ids:
                try:
                    server.cd(folder.path)
                except Exception:
                    not_accessible_folders.append(
                        "Folder %s is not accessible" % folder.name
                    )
                    continue
            if not_accessible_folders:
                server.close()
                raise exceptions.Warning("\n".join(not_accessible_folders))
            server.close()
            self.state = "done"

    def connect(self):
        """ Return appropriate object based on server_type """
        self.ensure_one()
        if self.server_type not in ("FTP", "ftpls", "sftp"):
            raise exceptions.Warning(_("Please select a server first"))
        if self.server_type == "FTP":
            return FTPServer(self.host, self.user, self.password, self.port)
        elif self.server_type == "sftp":
            return SFTPServer(self.host, self.user, self.password, self.port)
        else:
            raise exceptions.Warning(_("Only FTP and sftp for now"))
