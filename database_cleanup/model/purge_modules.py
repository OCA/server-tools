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

from openerp import pooler
from openerp.osv import orm, fields
from openerp.modules.module import get_module_path
from openerp.tools.translate import _
from openerp.addons.base.ir.ir_model import MODULE_UNINSTALL_FLAG


class IrModelConstraint(orm.Model):
    _inherit = 'ir.model.constraint'

    def _module_data_uninstall(self, cr, uid, ids, context=None):
        """this function crashes for constraints on undefined models"""
        for this in self.browse(cr, uid, ids, context=context):
            if not self.pool.get(this.model.model):
                ids.remove(this.id)
                this.unlink()
        return super(IrModelConstraint, self)._module_data_uninstall(
            cr, uid, ids, context=context)


class IrModelData(orm.Model):
    _inherit = 'ir.model.data'

    def _module_data_uninstall(self, cr, uid, modules_to_remove, context=None):
        """this function crashes for xmlids on undefined models or fields
        referring to undefined models"""
        if context is None:
            context = {}
        ids = self.search(cr, uid, [('module', 'in', modules_to_remove)])
        for this in self.browse(cr, uid, ids, context=context):
            if this.model == 'ir.model.fields':
                ctx = context.copy()
                ctx[MODULE_UNINSTALL_FLAG] = True
                field = self.pool[this.model].browse(
                    cr, uid, this.res_id, context=ctx)
                if not self.pool.get(field.model):
                    this.unlink()
                    continue
            if not self.pool.get(this.model):
                this.unlink()
        return super(IrModelData, self)._module_data_uninstall(
            cr, uid, modules_to_remove, context=context)


class CleanupPurgeLineModule(orm.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.module'

    _columns = {
        'wizard_id': fields.many2one(
            'cleanup.purge.wizard.module', 'Purge Wizard', readonly=True),
        }

    def purge(self, cr, uid, ids, context=None):
        """
        Uninstall modules upon manual confirmation, then reload
        the database.
        """
        module_pool = self.pool['ir.module.module']
        lines = self.browse(cr, uid, ids, context=context)
        module_names = [line.name for line in lines if not line.purged]
        module_ids = module_pool.search(
            cr, uid, [('name', 'in', module_names)], context=context)
        if not module_ids:
            return True
        self.logger.info('Purging modules %s', ', '.join(module_names))
        module_pool.write(
            cr, uid, module_ids, {'state': 'to remove'}, context=context)
        cr.commit()
        _db, _pool = pooler.restart_pool(cr.dbname, update_module=True)
        module_pool.unlink(cr, uid, module_ids, context=context)
        return self.write(cr, uid, ids, {'purged': True}, context=context)


class CleanupPurgeWizardModule(orm.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.module'

    def default_get(self, cr, uid, fields, context=None):
        res = super(CleanupPurgeWizardModule, self).default_get(
            cr, uid, fields, context=context)
        if 'name' in fields:
            res['name'] = _('Purge modules')
        return res

    def find(self, cr, uid, context=None):
        module_pool = self.pool['ir.module.module']
        module_ids = module_pool.search(cr, uid, [], context=context)
        res = []
        for module in module_pool.browse(cr, uid, module_ids, context=context):
            if get_module_path(module.name):
                continue
            if module.state == 'uninstalled':
                module_pool.unlink(cr, uid, module.id, context=context)
                continue
            res.append((0, 0, {'name': module.name}))

        if not res:
            raise orm.except_orm(
                _('Nothing to do'),
                _('No modules found to purge'))
        return res

    _columns = {
        'purge_line_ids': fields.one2many(
            'cleanup.purge.line.module',
            'wizard_id', 'Modules to purge'),
        }
