# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from ..tasks.filestore import FileStoreTask
from ..tasks.ftp import FtpTask
from ..tasks.sftp import SftpTask


class Location(models.Model):
    _name = 'external.file.location'
    _description = 'Location'

    name = fields.Char(string='Name', required=True)
    protocol = fields.Selection(selection='_get_protocol', required=True)
    address = fields.Char(
        string='Address')
    filestore_rootpath = fields.Char(
        string='FileStore Root Path',
        help="Server's root path")
    port = fields.Integer()
    login = fields.Char()
    password = fields.Char()
    task_ids = fields.One2many('external.file.task', 'location_id')
    hide_login = fields.Boolean(compute='_compute_protocol_dependent_fields')
    hide_password = fields.Boolean(compute='_compute_protocol_dependent_fields')
    hide_port = fields.Boolean(compute='_compute_protocol_dependent_fields')
    hide_address = fields.Boolean(compute='_compute_protocol_dependent_fields')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'external.file.location'))

    @api.model
    def _get_classes(self):
        "surcharge this method to add new protocols"
        return {
            # TODO: Migration to 11.0
            # 'ftp': ('FTP', FtpTask),
            # 'sftp': ('SFTP', SftpTask),
            # 'file_store': ('File Store', FileStoreTask),
        }

    @api.model
    def _get_protocol(self):
        protocols = self._get_classes()
        selection = []
        for key, val in protocols.items():
            selection.append((key, val[0]))
        return selection

    @api.depends('protocol')
    def _compute_protocol_dependent_fields(self):
        protocols = self._get_classes()
        active_protocols = [k for k, v in protocols.items()]
        if self.protocol in active_protocols:
            cls = protocols.get(self.protocol)[1]
            self.port = cls._default_port
            if cls._hide_login:
                self.hide_login = True
            else:
                self.hide_login = False
            if cls._hide_password:
                self.hide_password = True
            else:
                self.hide_password = False
            if cls._hide_port:
                self.hide_port = True
            else:
                self.hide_port = False
            if cls._hide_address:
                self.hide_address = True
            else:
                self.hide_address = False
        else:
            self.hide_login = True
            self.hide_password = True
            self.hide_port = True
            self.hide_address = True
