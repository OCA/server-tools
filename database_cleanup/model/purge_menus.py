# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
from openerp.osv import orm, fields
from openerp.tools.translate import _


class CleanupPurgeLineMenu(orm.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.menu'

    _columns = {
        'wizard_id': fields.many2one(
            'cleanup.purge.wizard.menu', 'Purge Wizard', readonly=True),
        'menu_id': fields.many2one('ir.ui.menu', 'Menu entry'),
    }

    def purge(self, cr, uid, ids, context=None):
        self.pool['ir.ui.menu'].unlink(
            cr, uid,
            [this.menu_id.id for this in self.browse(cr, uid, ids,
                                                     context=context)],
            context=context)
        return self.write(cr, uid, ids, {'purged': True}, context=context)


class CleanupPurgeWizardMenu(orm.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.menu'

    def default_get(self, cr, uid, fields, context=None):
        res = super(CleanupPurgeWizardMenu, self).default_get(
            cr, uid, fields, context=context)
        if 'name' in fields:
            res['name'] = _('Purge menus')
        return res

    def find(self, cr, uid, context=None):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        for menu in self.pool['ir.ui.menu'].browse(
                cr, uid, self.pool['ir.ui.menu'].search(
                    cr, uid, [], context=dict(
                        context or {}, active_test=False))):
            if not menu.action or menu.action.type != 'ir.actions.act_window':
                continue
            if not self.pool.get(menu.action.res_model):
                res.append((0, 0, {
                    'name': menu.complete_name,
                    'menu_id': menu.id,
                }))
        if not res:
            raise orm.except_orm(
                _('Nothing to do'),
                _('No dangling menu entries found'))
        return res

    _columns = {
        'purge_line_ids': fields.one2many(
            'cleanup.purge.line.menu',
            'wizard_id', 'Menus to purge'),
    }
