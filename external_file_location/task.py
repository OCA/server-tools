# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2015 Akretion (http://www.akretion.com).
#   @author Valentin CHEMIERE <valentin.chemiere@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
from .helper import itersubclasses
from .abstract_task import AbstractTask


class Task(models.Model):
    _name = 'external.file.task'
    _description = 'Description'

    name = fields.Char(required=True)
    method = fields.Selection(selection='_get_method', required=True,
                              help='procotol and trasmitting info')
    method_type = fields.Char()
    filename = fields.Char(help='File name which is imported')
    filepath = fields.Char(help='Path to imported file')
    location_id = fields.Many2one('external.file.location', string='Location',
                                  required=True)
    attachment_ids = fields.One2many('ir.attachment.metadata', 'task_id',
                                     string='Attachment')
    move_path = fields.Char(string='Move path',
                            help='Imported File will be moved to this path')
    md5_check = fields.Boolean(help='Control file integrity after import with'
                               ' a md5 file')
    after_import = fields.Selection(selection='_get_action',
                                    help='Action after import a file')

    def _get_action(self):
        return [('move', 'Move'), ('delete', 'Delete')]

    def _get_method(self):
        res = []
        for cls in itersubclasses(AbstractTask):
            if cls._synchronize_type \
                and ('protocol' not in self._context
                     or cls._key == self._context['protocol']):
                cls_info = (cls._key + '_' + cls._synchronize_type,
                            cls._name + ' ' + cls._synchronize_type)
                res.append(cls_info)
        return res

    @api.onchange('method')
    def onchange_method(self):
        if self.method:
            if 'import' in self.method:
                self.method_type = 'import'
            elif 'export' in self.method:
                self.method_type = 'export'

    @api.model
    def _run(self, domain=None):
        if not domain:
            domain = []
        tasks = self.env['external.file.task'].search(domain)
        tasks.run()

    @api.one
    def run(self):
        for cls in itersubclasses(AbstractTask):
            if cls._synchronize_type and \
                    cls._key + '_' + cls._synchronize_type == self.method:
                method_class = cls
        config = {
            'host': self.location_id.address,
            'user': self.location_id.login,
            'pwd': self.location_id.password,
            'port': self.location_id.port,
            'allow_dir_creation': False,
            'file_name': self.filename,
            'path': self.filepath,
            'attachment_ids': self.attachment_ids,
            'task': self,
            'move_path': self.move_path,
            'after_import': self.after_import,
            'md5_check': self.md5_check,
            }
        conn = method_class(self.env, config)
        conn.run()
