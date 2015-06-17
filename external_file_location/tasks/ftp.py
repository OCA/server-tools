# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from .abstract_fs import AbstractFSTask
from base64 import b64decode
from fs import ftpfs
import logging
_logger = logging.getLogger(__name__)


class FtpTask(AbstractFSTask):

    _key = 'ftp'
    _name = 'FTP'
    _synchronize_type = None
    _default_port = 21
    _hide_login = False
    _hide_password = False
    _hide_port = False


class FtpImportTask(FtpTask):

    _synchronize_type = 'import'

    def run(self):
        att_ids = []
        with ftpfs.FTPFS(self.host, self.user, self.pwd,
                         port=self.port) as ftp_conn:
            files_to_process = self._get_files(ftp_conn, self.path)
            for file_to_process in files_to_process:
                att_ids.append(self._process_file(ftp_conn, file_to_process))
        return att_ids

class FtpExportTask(FtpTask):

    _synchronize_type = 'export'

    def run(self, async=True):
        import ipdb; ipdb.set_trace()
        for attachment in self.attachment_ids:
            if attachment.state in ('pending', 'failed'):
                self.attachment_id = attachment
                with ftpfs.FTPFS(self.host, self.user, self.pwd,
                                 port=self.port) as ftp_conn:
                    self._upload_file(ftp_conn, self.host, self.port,
                                      self.user, self.pwd, self.path,
                                      attachment.datas_fname,
                                      b64decode(attachment.datas))
