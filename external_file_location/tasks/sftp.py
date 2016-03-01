# coding: utf-8
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .abstract_fs import AbstractFSTask
from base64 import b64decode
from fs import sftpfs
import logging
_logger = logging.getLogger(__name__)


class SftpTask(AbstractFSTask):

    _key = 'sftp'
    _name = 'SFTP'
    _synchronize_type = None
    _default_port = 22
    _hide_login = False
    _hide_password = False
    _hide_port = False


class SftpImportTask(SftpTask):

    _synchronize_type = 'import'

    def run(self):
        connection_string = "{}:{}".format(self.host, self.port)
        root = "/"
        att_ids = []
        with sftpfs.SFTPFS(connection=connection_string,
                           root_path=root,
                           username=self.user,
                           password=self.pwd) as sftp_conn:
            files_to_process = self._get_files(sftp_conn, self.path)
            for file_to_process in files_to_process:
                att_ids.append(self._process_file(sftp_conn, file_to_process))
        return att_ids


class SftpExportTask(SftpTask):

    _synchronize_type = 'export'

    def run(self, async=True):
        for attachment in self.attachment_ids:
            if attachment.state in ('pending', 'failed'):
                self.attachment_id = attachment
                connection_string = "{}:{}".format(self.host, self.port)
                with sftpfs.SFTPFS(connection=connection_string,
                                   username=self.user,
                                   password=self.pwd) as sftp_conn:
                    datas = b64decode(attachment.datas)
                    self._upload_file(sftp_conn, self.host, self.port,
                                      self.user, self.pwd, self.path,
                                      attachment.datas_fname, datas)
