# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from ftplib import FTP, error_perm

from .abstract_ftp_server import AbstractFTPServer


class FTPServer(AbstractFTPServer):

    def connect(self, host, port, user, password):
        """ Connect to server """
        self.server = FTP()
        # Init step by step
        self.server.connect(host=self.host, port=self.port)
        self.server.login(user=self.user, passwd=self.password)
        return self

    def close(self):
        """ Close connection """
        self.server.quit()
        self.server = None
        self.host = None
        self.username = None
        self.password = None
        self.port = None

    def putfo(self, file_like, name):
        """Transfer file-like object to server

           name: filename+extension for file at server
           file_like: byte object, content of which
           will appear in server as name

           Example

           bytes_ = b'abc def'
           name = "abc.txt"
           self.putfo(io.BytesIO(bytes_), name)
        """
        self.server.storbinary("STOR " + name, file_like)

    def put(self, filepath, name):
        """Transfer file object to server

           name: filename+extension for file at server
           filepath: path + the actual file you are putting
        """
        with open(filepath, "rb") as file:
            self.server.storbinary("STOR " + name, file)

    def getfo(self, filepath, name):
        """Get file-like object from server

           name: containt of file in filepath in bytes
           filepath: filename+extension for file at server
        """
        self.server.retrbinary("RETR " + filepath, name.write)

    def remove(self, file):
        """Remove file from server"""
        self.server.delete(file)

    def listdir(self, path=""):
        """ List directory in path """
        files = []
        try:
            files = self.server.nlst(path)
        except error_perm:
            files = []
        return files

    def cd(self, path):
        """ Change directory """
        self.server.cwd(path)

    def exists(self, file, path=""):
        """ See if file exists in path """
        return file in self.server.nlst(path)
