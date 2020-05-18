# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from ftplib import FTP_TLS

from .ftp_server import FTPServer


class FTPTLSServer(FTPServer):

    def connect(self, host, port, user, password):
        """ Connect to server """
        self.server = FTP_TLS()
        # Init step by step
        self.server.connect(host=self.host, port=self.port)
        self.server.login(user=self.user, passwd=self.password)
        return self
