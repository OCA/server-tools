# -*- coding: utf-8 -*-
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import config
from dropbox import exceptions as dropbox_exceptions
from odoo.exceptions import ValidationError
from odoo import _
import logging
_logger = logging.getLogger(__name__)
try:
    import dropbox
except ImportError:
    _logger.debug('Cannot import `dropbox`.')


class DropboxTask:
    _key = 'dropbox'
    _name = 'DROPBOX'
    _synchronize_type = None
    _default_port = False
    _hide_login = True
    _hide_password = True
    _hide_port = True
    _hide_address = True

    def __init__(self, location):
        self.conn = dropbox.Dropbox(location)

    def setcontents(self, path, data=None):
        try:
            path = '/' + (path or '').lstrip('/')
            self.conn.files_upload(data, path)
        except dropbox_exceptions.AuthError:
            raise ValidationError(_("Dropbox: Access Key not valid!"))
        except dropbox_exceptions.BadInputError:
            raise ValidationError(_("Dropbox: Access Key is malformed!"))

    @staticmethod
    def connect(location):
        if config.get('dropbox_access_key_id'):
            access_key_id = config.get('dropbox_access_key_id')
        else:
            access_key_id = location.access_key_id
        conn = DropboxTask(access_key_id)
        return conn
