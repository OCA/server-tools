# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from contextlib import contextmanager
from io import StringIO

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import paramiko
except ImportError:
    _logger.info('`paramiko` Python library is not installed')


class ConnectorSftp(models.Model):
    _name = 'connector.sftp'
    _inherit = 'external.system.adapter'
    _description = 'SFTP Connector'

    @api.multi
    def external_get_client(self):
        """Return a usable SFTP client."""
        super(ConnectorSftp, self).external_get_client()
        transport = paramiko.Transport((
            self.host, self.port,
        ))
        fingerprint = self.fingerprint or None
        if self.private_key:
            with StringIO(self.private_key) as io:
                private_key = paramiko.RSAKey.from_private_key(
                    io, self.private_key_password or None,
                )
        else:
            private_key = None
        transport.connect(
            hostkey=fingerprint,
            username=self.username,
            password=self.password or None,
            pkey=private_key,
        )
        client = paramiko.SFTPClient.from_transport(transport)
        if self.remote_path:
            client.chdir(self.remote_path)
        return client

    @api.multi
    def external_destroy_client(self, client):
        """Close the connection."""
        super(ConnectorSftp, self).external_destroy_client(client)
        if client:
            client.close()

    @api.multi
    def external_test_connection(self):
        with self.client() as client:
            if not client:
                raise ValidationError(_(
                    'The SFTP connection was not able to be established.',
                ))
        super(ConnectorSftp, self).external_test_connection()

    @api.multi
    def list_dir(self, path):
        """Return a list containing the names of the entries in ``path``

        The list is in arbitrary order. It does not include the special
        entries ``'.'`` and ``'..'`` even if they are present in the folder.
        This method is meant to mirror the ``os.listdir`` as closely as
        possible.

        Params:
            path (str): Path to list

        Returns:
            list: of names in path
        """
        with self.client() as client:
            return client.listdir(path)

    @api.multi
    def stat(self, path):
        """Retrieve information about a file on remote system. Return value is
        an obj whose attributes correspond to the structure of the stdlib
        ``os.stat``, except that it may be lacking fields due to SFTP server
        configuration.

        Unlike a Python stat object, the result may not be accessed as a tuple.
        This is mostly due to the author’s slack factor.

        The fields supported are: ``st_mode``, ``st_size``, ``st_uid``,
        `st_gid``, ``st_atime``, and ``st_mtime``.

        Params:
            path (str): Filename to stat

        Returns:
            paramiko.SFTPAttributes: object containing attributes about file.
        """
        with self.client() as client:
            return client.stat(path)

    @api.multi
    @contextmanager
    def open(self, file_name, mode='r', buff_size=-1):
        """Open file on remote server. Mimicks python open function, and result
        can be used as a context manager.

        Params:
            file_name (str): File to open
            mode (str); How to open file, reference Python open
            buff_size (int): Desired buffering

        Returns:
            paramiko.SFTPFile object: representing the open file

        Raises:
            IOError: if the file cannot be opened
        """
        with self.client() as client:
            with client.open(file_name, mode, buff_size) as fh:
                yield fh

    @api.multi
    def delete(self, path):
        """Remove the file at the given path. Does not work on directories.

        Params:
            path (str): Path of file to delete.

        Raises:
            IOError: if path refers to a directory.
        """
        with self.client() as client:
            return client.unlink(path)

    @api.multi
    def symlink(self, source, dest):
        """Create a symbolic link of the source path at destination on remote.

        Params:
            source (str): Path of original file
            dest (str): Path of new symlink
        """
        with self.client() as client:
            return client.symlink(source, dest)
