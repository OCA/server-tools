# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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

import logging
from openerp.osv import orm, fields


class CleanupPurgeLine(orm.AbstractModel):
    """ Abstract base class for the purge wizard lines """
    _name = 'cleanup.purge.line'
    _order = 'name'
    _columns = {
        'name': fields.char('Name', size=256, readonly=True),
        'purged': fields.boolean('Purged', readonly=True),
        }

    logger = logging.getLogger('openerp.addons.database_cleanup')

    def purge(self, cr, uid, ids, context=None):
        raise NotImplementedError


class PurgeWizard(orm.AbstractModel):
    """ Abstract base class for the purge wizards """
    _name = 'cleanup.purge.wizard'

    def default_get(self, cr, uid, fields, context=None):
        res = super(PurgeWizard, self).default_get(
            cr, uid, fields, context=context)
        if 'purge_line_ids' in fields:
            res['purge_line_ids'] = self.find(cr, uid, context=None)
        return res

    def find(self, cr, uid, ids, context=None):
        raise NotImplementedError

    def purge_all(self, cr, uid, ids, context=None):
        line_pool = self.pool[self._columns['purge_line_ids']._obj]
        for wizard in self.browse(cr, uid, ids, context=context):
            line_pool.purge(
                cr, uid, [line.id for line in wizard.purge_line_ids],
                context=context)
        return True

    def get_wizard_action(self, cr, uid, context=None):
        wizard_id = self.create(cr, uid, {}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'views': [(False, 'form')],
            'res_model': self._name,
            'res_id': wizard_id,
            'flags': {
                'action_buttons': False,
                'sidebar': False,
            },
        }

    def select_lines(self, cr, uid, ids, context=None):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Select lines to purge',
            'views': [(False, 'tree'), (False, 'form')],
            'res_model': self._columns['purge_line_ids']._obj,
            'domain': [('wizard_id', 'in', ids)],
        }

    _columns = {
        'name': fields.char('Name', size=64, readonly=True),
        }
