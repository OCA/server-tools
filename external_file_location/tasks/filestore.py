# coding: utf-8
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .abstract_fs import AbstractFSTask
from base64 import b64decode
from fs import osfs
import logging
_logger = logging.getLogger(__name__)


class FileStoreTask(AbstractFSTask):

    _key = 'filestore'
    _name = 'File Store'
    _synchronize_type = None
    _default_port = None
    _hide_login = True
    _hide_password = True
    _hide_port = True


class FileStoreImportTask(FileStoreTask):

    _synchronize_type = 'import'

    def run(self):
        att_ids = []
        with osfs.OSFS(self.host) as fs_conn:
            files_to_process = self._get_files(fs_conn, self.path)
            for file_to_process in files_to_process:
                att_ids.append(self._process_file(fs_conn, file_to_process))
        return att_ids


class FileStoreExportTask(FileStoreTask):

    _synchronize_type = 'export'

    def run(self, async=True):
        for attachment in self.attachment_ids:
            if attachment.state in ('pending', 'failed'):
                self.attachment_id = attachment
                with osfs.OSFS(self.host) as fs_conn:
                    self._upload_file(fs_conn,
                                      self.host,
                                      self.port,
                                      self.user,
                                      self.pwd,
                                      self.path,
                                      attachment.datas_fname,
                                      b64decode(attachment.datas))
