# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
import os

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import human_size

_logger = logging.getLogger(__name__)


class IrFilesystemDirectoryLine(models.TransientModel):
    _name = 'ir.filesystem.file'
    _description = 'File in filesystem'

    name = fields.Char(required=True)
    filename = fields.Char()
    file_content = fields.Binary(compute='_compute_file')
    stored_filename = fields.Char()
    directory_id = fields.Many2one(
        'ir.filesystem.directory',
        string='Directory',
    )

    @api.multi
    def _file_read(self, fname, bin_size=False):

        def file_not_found(fname):
            raise UserError(_(
                '''Error while reading file %s.
                Maybe it was removed or permission is changed.
                Please refresh the list.''' % fname))

        self.ensure_one()
        r = ''
        directory = self.directory_id.get_dir()
        full_path = directory + fname
        if not (directory and os.path.isfile(full_path)):
            file_not_found(fname)
        try:
            if bin_size:
                r = human_size(os.path.getsize(full_path))
            else:
                r = base64.b64encode(open(full_path, 'rb').read())
        except (IOError, OSError):
            _logger.info("_read_file reading %s", fname, exc_info=True)
        return r

    @api.depends('stored_filename')
    def _compute_file(self):
        bin_size = self.env.context.get('bin_size')
        for line in self:
            if line.stored_filename:
                content = line._file_read(line.stored_filename, bin_size)
                line.file_content = content
