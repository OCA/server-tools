# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import pysftp

from .abstract_ftp_server import AbstractFTPServer


class SFTPServer(AbstractFTPServer):

    def connect(self, host, port, user, password):
        """ Connect to object """
        # TODO: make this secure
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        self.server = pysftp.Connection(host, port, user, password, cnopts=cnopts)
        return self

    def close(self):
        """ Close connection """
        self.server.close()
        self.server = None

    def putfo(self, file_like, name):
        """Transfer file-like object to server

           name: filename+extension for file at server
           file_like: byte object, content of which
           will appear in server as name
        """
        self.server.putfo(file_like, name)

    def put(self, filepath, name):
        """Transfer file object to server

           name: filename+extension for file at server
           filepath: filepath_to_file, content of which
           will appear in server as name
        """
        self.server.put(filepath, name)

    def getfo(self, name, file_like):
        """Get file from server

        name: filename of file to retrieve
        file_like: byte object to save containt
        of filename
        """
        self.server.getfo(name, file_like)

    def remove(self, file):
        """Remove file from server"""
        self.server.remove(file)

    def listdir(self, path=""):
        """ List directory in path """
        return self.server.listdir(path)

    def cd(self, path):
        """ Change directory """
        self.server.chdir(path)

    def exists(self, file, path=""):
        """ See if file exists in path """
        return self.server.exists(path + file)
