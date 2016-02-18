# -*- coding: utf-8 -*-
# © 2016-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import paramiko


class ConnectorSftp(models.Model):
    _name = 'connector.sftp'
    _description = 'SFTP Connector'

    name = fields.Char(
        required=True,
    )
    host = fields.Char(
        required=True,
    )
    port = fields.Integer(
        required=True,
        default=22,
    )
    username = fields.Char(
        required=True,
    )
    password = fields.Char()
    private_key = fields.Text()
    host_key = fields.Text()
    ignore_host_key = fields.Boolean()
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        inverse_name='sftp_connector_ids',
        required=True,
    )
    transport = fields.Binary(
        store=False,
    )
    client = fields.Binary(
        store=False,
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Connection name must be unique.'),
    ]

    @api.multi
    def _create_client(self):
        '''
        Establish SSH Transport and SFTP client.

        Raises:
            :class:``paramiko.SSHException`` if the SSH2 negotiation fails,
                the host key supplied by the server is incorrect, or
                authentication fails.
        '''
        self.ensure_one()
        if not self.transport or not self.client:
            self.transport = paramiko.Transport((
                self.host, self.port,
            ))
            if self.ignore_host_key:
                host_key = None
            else:
                host_key = self.host_key if self.host_key else None
            self.transport.connect(
                hostkey=host_key,
                username=self.username,
                password=self.password,
                pkey=self.private_key if self.private_key else None,
            )
            self.client = paramiko.SFTPClient.from_transport(
                self.transport
            )

    @api.multi
    def _sftp_listdir(self, path):
        '''
        Return a list containing the names of the entries in ``path``

        The list is in arbitrary order. It does not include the special
        entries ``'.'`` and ``'..'`` even if they are present in the folder.
        This method is meant to mirror the ``os.listdir`` as closely as
        possible.

        Params:
            path: str Path to list

        Returns:
            list of names in path
        '''
        self._create_client()
        return self.client.listdir(path)

    @api.multi
    def _sftp_stat(self, path):
        '''
        Retrieve information about a file on remote system. Return value is
        an obj whose attributes correspond to the structure of the stdlib
        ``os.stat``, except that it may be lacking fields due to SFTP server
        configuration.

        Unlike a Python stat object, the result may not be accessed as a tuple.
        This is mostly due to the author’s slack factor.

        The fields supported are: ``st_mode``, ``st_size``, ``st_uid``,
        `st_gid``, ``st_atime``, and ``st_mtime``.

        Params:
            path: str Filename to stat

        Returns:
            :class:``paramiko.SFTPAttributes`` object containing attrs about
                file
        '''
        self._create_client()
        return self.client.stat(path)

    @api.multi
    def _sftp_open(self, file_name, mode='r', buff_size=-1):
        '''
        Open file on remote server. Mimicks python open function, and result
        can be used as a context manager.

        Params:
            file_name: str File to open
            mode: str How to open file, reference Python open
            buff_size: int Desired buffering

        Returns:
            :class:``paramiko.SFTPFile object`` representing the open file

        Raises:
            IOError: if the file cannot be opened
        '''
        self._create_client()
        return self.client.open(file_name, mode, buff_size)

    @api.multi
    def _sftp_unlink(self, path):
        '''
        Remove the file at the given path. Does not work on dirs

        Params:
            path: str Path to file to delete

        Raises:
            IOError: if path refers to a directory
        '''
        self._create_client()
        return self.client.unlink(path)

    @api.multi
    def _sftp_symlink(self, source, dest):
        '''
        Create a symbolic link of the source path at destination on remote

        Params:
            source: str Path of original file
            dest: str Path of new symlink
        '''
        self._create_client()
        return self.client.symlink(source, dest)
