# coding: utf-8
# @ 2015 Valentin CHEMIERE @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from ..tasks.abstract_task import AbstractTask
from .helper import itersubclasses


class Location(models.Model):
    _name = 'external.file.location'
    _description = 'Description'

    name = fields.Char(string='Name', required=True)
    protocol = fields.Selection(selection='_get_protocol', required=True)
    address = fields.Char(string='Address', required=True)
    port = fields.Integer()
    login = fields.Char()
    password = fields.Char()
    task_ids = fields.One2many('external.file.task', 'location_id')
    hide_login = fields.Boolean()
    hide_password = fields.Boolean()
    hide_port = fields.Boolean()

    def _get_protocol(self):
        res = []
        for cls in itersubclasses(AbstractTask):
            if not cls._synchronize_type:
                cls_info = (cls._key, cls._name)
                res.append(cls_info)
            elif not cls._synchronize_type and cls._key and cls._name:
                pass
        return res

    @api.onchange('protocol')
    def onchange_protocol(self):
        for cls in itersubclasses(AbstractTask):
            if cls._key == self.protocol:
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
