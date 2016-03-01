# coding: utf-8
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import os
import fnmatch

from openerp.tools.safe_eval import safe_eval as eval

from ..abstract_task import AbstractTask

_logger = logging.getLogger(__name__)


class AbstractFSTask(AbstractTask):

    _name = None
    _key = None
    _synchronize_type = None
    _default_port = None

    def __init__(self, env, config):
        self.env = env
        self.host = config.get('host', '')
        self.user = config.get('user', '')
        self.pwd = config.get('pwd', '')
        self.port = config.get('port', '')
        self.allow_dir_creation = config.get('allow_dir_creation', '')
        self.file_name = config.get('file_name', '')
        self.path = config.get('path') or '.'
        self.move_path = config.get('move_path', '')
        self.new_name = config.get('new_name', '')
        self.after_import = config.get('after_import', False)
        self.attachment_ids = config.get('attachment_ids', False)
        self.task = config.get('task', False)
        self.ext_hash = False
        self.md5_check = config.get('md5_check', False)

    def _handle_new_source(self, fs_conn, download_directory, file_name,
                           move_directory):
        """open and read given file into create_file method,
           move file if move_directory is given"""
        with fs_conn.open(self._source_name(download_directory, file_name),
                          "rb") as fileobj:
            data = fileobj.read()
        return self.create_file(file_name, data)

    def _source_name(self, download_directory, file_name):
        """helper to get the full name"""
        return os.path.join(download_directory, file_name)

    def _move_file(self, fs_conn, source, target):
        """Moves a file on the server"""
        _logger.info('Moving file %s %s' % (source, target))
        fs_conn.rename(source, target)
        if self.md5_check:
            fs_conn.rename(source + '.md5', target + '.md5')

    def _delete_file(self, fs_conn, source):
        """Deletes a file from the server"""
        _logger.info('Deleting file %s' % source)
        fs_conn.remove(source)
        if self.md5_check:
            fs_conn.remove(source + '.md5')

    def _get_hash(self, file_name, fs_conn):
        hash_file_name = file_name + '.md5'
        with fs_conn.open(hash_file_name, 'rb') as f:
            return f.read().rstrip('\r\n')

    def _get_files(self, conn, path):
        process_files = []
        files_list = conn.listdir(path)
        pattern = self.file_name
        for file_name in fnmatch.filter(files_list, pattern):
            source_name = self._source_name(self.path, file_name)
            process_files.append((file_name, source_name))
        return process_files

    def _process_file(self, conn, file_to_process):
            if self.md5_check:
                self.ext_hash = self._get_hash(file_to_process[1], conn)
            att_id = self._handle_new_source(
                conn,
                self.path,
                self.file_name,
                self.move_path)
            ('rename', 'Rename'),
                ('move', 'Move'),
                ('move_rename', 'Move & Rename'),

            move = 'move' in self.after_import
            rename = 'rename' in self.after_import

            # Move/delete files only after all files have been processed.
            if self.after_import == 'delete':
                self._delete_file(conn, file_to_process[1])
            elif rename or move:
                new_name = file_to_process[0]
                move_path = self.path
                if rename and self.new_name:
                    #TODO select correspondig attachement_id
                    localdict = {'obj': self.attachment_ids[0]}
                    new_name = eval(tax.python_compute, localdict,
                                    mode="exec", nocopy=True)
                if self.move_path and not conn.exists(self.move_path):
                    conn.makedir(self.move_path)
                    move_path = self.move_path
                self._move_file(
                    conn,
                    file_to_process[1],
                    self._source_name(move_path, new_name))
            return att_id

    def _handle_existing_target(self, fs_conn, target_name, filedata):
        raise Exception("%s already exists" % target_name)

    def _handle_new_target(self, fs_conn, target_name, filedata):
        try:
            with fs_conn.open(target_name, mode='wb') as fileobj:
                fileobj.write(filedata)
                _logger.info('wrote %s, size %d', target_name, len(filedata))
            self.attachment_id.state = 'done'
            self.attachment_id.state_message = ''
        except IOError:
            self.attachment_id.state = 'failed'
            self.attachment_id.state_message = (
                'The directory doesn\'t exist or had insufficient rights')

    def _target_name(self, fs_conn, upload_directory, filename):
        return os.path.join(upload_directory, filename)

    def _upload_file(self, conn, host, port, user, pwd,
                     path, filename, filedata):
        upload_directory = path or '.'
        target_name = self._target_name(conn,
                                        upload_directory,
                                        filename)
        if conn.isfile(target_name):
            self._handle_existing_target(conn, target_name, filedata)
        else:
            self._handle_new_target(conn, target_name, filedata)
