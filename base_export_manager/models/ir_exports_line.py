# -*- coding: utf-8 -*-
# Python source code encoding : https://www.python.org/dev/peps/pep-0263/
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright :
#        (c) 2015 Antiun Ingenieria, SL (Madrid, Spain, http://www.antiun.com)
#                 Antonio Espinosa <antonioea@antiun.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions
from openerp.tools.translate import _


class IrExportsLine(models.Model):
    _inherit = 'ir.exports.line'
    _order = 'sequence,id'

    sequence = fields.Integer()
    label = fields.Char(string='Label', compute="_get_label")

    def _get_label_string(self):
        self.ensure_one()
        model_name = self.export_id.resource
        label = ''
        if not self.name:
            return False
        for field in self.name.split('/'):
            model = self.env['ir.model'].search([('model', '=', model_name)])
            field_obj = model.field_id.filtered(lambda r: r.name == field)
            if not field_obj:
                return False
            label = label + _(field_obj.field_description) + '/'
            model_name = field_obj.relation
        return label.rstrip('/') + ' (' + self.name + ')'

    @api.one
    @api.constrains('name')
    def _check_name(self):
        if not self._get_label_string():
            raise exceptions.ValidationError(
                _("Field '%s' does not exist") % self.name)
        lines = self.search([('export_id', '=', self.export_id.id),
                             ('name', '=', self.name)])
        if len(lines) > 1:
            raise exceptions.ValidationError(
                _("Field '%s' already exists") % self.name)

    @api.one
    @api.depends('name')
    def _get_label(self):
        self.label = self._get_label_string()

    @api.onchange('name')
    def _onchange_name(self):
        self.label = self._get_label_string()
