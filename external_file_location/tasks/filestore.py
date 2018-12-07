# coding: utf-8
# @ 2016 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
_logger = logging.getLogger(__name__)

try:
    from fs import osfs
except ImportError:
    _logger.debug('Cannot `import fs`.')


# TODO: Migration to 11.0
class FileStoreTask(osfs.OSFS):

    _key = 'filestore'
    _name = 'File Store'
    _default_port = None
    _hide_login = True
    _hide_password = True
    _hide_port = True
    _hide_address = False

    @staticmethod
    def connect(location):
        rootpath = location.filestore_rootpath or '/'
        conn = FileStoreTask(rootpath)
        return conn
