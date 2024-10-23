# -*- coding: utf-8 -*-
# Copyright 2015 Anubía, soluciones en la nube,SL (http://www.anubia.es)
# Copyright 2017 Onestein (http://www.onestein.eu)
# Copyright 2021 ArcheTI (http://www.archeti.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from lxml import etree
from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class IrModel(models.Model):
    _inherit = 'ir.model'

    import_group_id = fields.Many2one(
        comodel_name='res.groups')


class Base(models.AbstractModel):
    _inherit = 'base'

    def _allow_import(self):
        current_user = self.env.user
        allowed_group = 'base_import_security_group.group_import_csv'
        allowed_group_id = self.env.ref(
            allowed_group,
            raise_if_not_found=False
        )
        model_group_id = self.env['ir.model'].search([
            ('model', '=', self._name)]).import_group_id
        return (
            not allowed_group_id
            or current_user.has_group(allowed_group)
            or current_user in model_group_id.users
        )

    @api.model
    def load(self, fields, data):
        '''Overriding this method we only allow its execution
        if current user belongs to the group allowed for CSV data import.
        An exception is raised otherwise, and also log the import attempt.
        '''
        if self._allow_import():
            res = super(Base, self).load(fields=fields, data=data)
        else:
            msg = ('User (ID: %s) is not allowed to import data '
                   'in model %s.') % (self.env.uid, self._name)
            _logger.info(msg)
            messages = []
            info = {}
            messages.append(
                dict(info, type='error', message=msg, moreinfo=None))
            res = {'ids': None, 'messages': messages}
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if view_type not in ('tree', 'kanban'):
            return result
        view = etree.fromstring(result['arch'])
        if view.get('import'):
            return result
        if not self._allow_import():
            view.set('import', 'false')
            result['arch'] = etree.tostring(view, encoding='unicode')
        return result
