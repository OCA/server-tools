# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, fields, models
from odoo.exceptions import UserError

from ..lib.ftp_server import FTPServer
from ..lib.ftp_tls_server import FTPTLSServer
from ..lib.mock_server import MockServer
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
        selection=[
            ("ftp", "FTP"),
            ("ftpls", "FTP_TLS"),
            ("sftp", "SFTP"),
            ("mock", "Mock"),
        ],
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
            raise UserError(_("Make sure that required info is set"))
        try:
            server = self.connect()
        except Exception as e:
            raise UserError(str(e))
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
                raise UserError("\n".join(not_accessible_folders))
            server.close()
            self.state = "done"

    def connect(self):
        """ Return appropriate object based on server_type """
        self.ensure_one()
        server = self._make_server_instance()
        server.connect(self.host, self.port, self.user, self.password)
        return server

    def _make_server_instance(self):
        """Return server class for selected type."""
        if self.server_type == "ftp":
            return FTPServer()
        elif self.server_type == "ftptls":
            return FTPTLSServer()
        elif self.server_type == "sftp":
            return SFTPServer()
        elif self.server_type == "mock":
            return MockServer()
        else:
            raise UserError(_("Unsupported FTP server type %s") % self.server_type)
