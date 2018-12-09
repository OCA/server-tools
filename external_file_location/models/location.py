# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class Location(models.Model):
    _name = 'external.file.location'
    _description = 'Location'

    name = fields.Char(required=True)
    protocol = fields.Selection(selection='_get_protocol', required=True)
    address = fields.Char()
    filestore_rootpath = fields.Char(
        string='FileStore Root Path',
        help="Server's root path")
    port = fields.Integer()
    login = fields.Char()
    password = fields.Char()
    task_ids = fields.One2many('external.file.task', 'location_id')
    hide_login = fields.Boolean(compute='_compute_protocol_dependent_fields')
    hide_password = fields.Boolean(
        compute='_compute_protocol_dependent_fields')
    hide_port = fields.Boolean(compute='_compute_protocol_dependent_fields')
    hide_address = fields.Boolean(compute='_compute_protocol_dependent_fields')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'external.file.location'))

    @api.model
    def _get_classes(self):
        """ override this method to add new protocols """
        return {}

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
        if self.protocol in protocols:
            cls = protocols.get(self.protocol)[1]
            self.port = cls._default_port
            self.hide_login = bool(cls._hide_login)
            self.hide_password = bool(cls._hide_password)
            self.hide_port = bool(cls._hide_port)
            self.hide_address = bool(cls._hide_address)
        else:
            self.hide_login = True
            self.hide_password = True
            self.hide_port = True
            self.hide_address = True
