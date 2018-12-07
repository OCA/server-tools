# coding: utf-8
# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
_logger = logging.getLogger(__name__)

try:
    from fs import ftpfs
except ImportError:
    _logger.debug('Cannot `import fs`.')


# TODO: Migration to 11.0
class FtpTask(ftpfs.FTPFS):

    _key = 'sftp'
    _name = 'SFTP'
    _synchronize_type = None
    _default_port = 22
    _hide_login = False
    _hide_password = False
    _hide_port = False
    _hide_address = False

    @staticmethod
    def connect(location):
        conn = FtpTask(location.address,
                       location.login,
                       location.password,
                       location.port)
        return conn
