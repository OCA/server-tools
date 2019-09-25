# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from glob import glob
from os.path import basename, isfile, join, exists, normpath, realpath

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class IrFilesystemDirectory(models.Model):
    _name = 'ir.filesystem.directory'
    _description = 'Filesystem Directory'

    name = fields.Char(required=True, copy=False)
    directory = fields.Char()
    file_ids = fields.One2many(
        'ir.filesystem.file',
        compute='_compute_file_ids',
        string='Files',
    )
    file_count = fields.Integer(
        compute='_compute_file_count',
        string="# Files",
    )
    files_filter = fields.Char()

    @api.multi
    def get_dir(self):
        self.ensure_one()
        directory = self.directory or ''
        # adds slash character at the end if missing
        return join(directory, '')

    @api.multi
    def _compute_file_ids(self):
        File = self.env['ir.filesystem.file']
        for directory in self:
            directory.file_ids = None
            if directory.get_dir():
                for file_name in directory._get_directory_files():
                    directory.file_ids += File.create({
                        'name': file_name,
                        'filename': file_name,
                        'stored_filename': file_name,
                        'directory_id': directory.id,
                    })

    @api.onchange('directory')
    def onchange_directory(self):
        if self.directory and not exists(self.directory):
            raise UserError(_('Directory does not exist'))

    @api.multi
    def _compute_file_count(self):
        for directory in self:
            directory.file_count = len(directory.file_ids)

    @api.multi
    def _get_directory_files(self):

        def get_files(directory, files_filter):
            glob_path = join(directory, files_filter)
            content = glob(glob_path)
            for full_path in content:
                file_name = basename(full_path)
                # Symbolic links and up-level references are not considered
                norm_path = normpath(realpath(full_path))
                if norm_path in full_path:
                    if isfile(full_path) and file_name[0] != '.':
                        files.append(file_name)

        self.ensure_one()
        files = []
        if self.get_dir() and exists(self.get_dir()):
            try:
                get_files(self.get_dir(), self.files_filter or '*')
            except (IOError, OSError):
                _logger.info(
                    "_get_directory_files reading %s",
                    self.get_dir(),
                    exc_info=True
                )
        return files

    @api.multi
    def reload(self):
        self.onchange_directory()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super(IrFilesystemDirectory, self).copy(default=default)
