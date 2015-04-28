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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class CleanupPurgeLineData(orm.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.data'

    _columns = {
        'data_id': fields.many2one(
            'ir.model.data', 'Data entry',
            ondelete='SET NULL'),
        'wizard_id': fields.many2one(
            'cleanup.purge.wizard.data', 'Purge Wizard', readonly=True),
        }

    def purge(self, cr, uid, ids, context=None):
        """
        Unlink data entries upon manual confirmation.
        """
        data_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.purged or not line.data_id:
                continue
            data_ids.append(line.data_id.id)
            self.logger.info('Purging data entry: %s', line.name)
        self.pool['ir.model.data'].unlink(cr, uid, data_ids, context=context)
        return self.write(cr, uid, ids, {'purged': True}, context=context)


class CleanupPurgeWizardData(orm.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.data'

    def default_get(self, cr, uid, fields, context=None):
        res = super(CleanupPurgeWizardData, self).default_get(
            cr, uid, fields, context=context)
        if 'name' in fields:
            res['name'] = _('Purge data')
        return res

    def find(self, cr, uid, context=None):
        """
        Collect all rows from ir_model_data that refer
        to a nonexisting model, or to a nonexisting
        row in the model's table.
        """
        res = []
        data_pool = self.pool['ir.model.data']
        data_ids = []
        unknown_models = []
        cr.execute("""SELECT DISTINCT(model) FROM ir_model_data""")
        for (model,) in cr.fetchall():
            if not model:
                continue
            if not self.pool.get(model):
                unknown_models.append(model)
                continue
            cr.execute(
                """
                SELECT id FROM ir_model_data
                WHERE model = %%s
                AND res_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT id FROM %s WHERE id=ir_model_data.res_id)
                """ % self.pool[model]._table, (model,))
            data_ids += [data_row[0] for data_row in cr.fetchall()]
        data_ids += data_pool.search(
            cr, uid, [('model', 'in', unknown_models)], context=context)
        for data in data_pool.browse(cr, uid, data_ids, context=context):
            res.append((0, 0, {
                        'data_id': data.id,
                        'name': "%s.%s, object of type %s" % (
                            data.module, data.name, data.model)}))
        if not res:
            raise orm.except_orm(
                _('Nothing to do'),
                _('No orphaned data entries found'))
        return res

    _columns = {
        'purge_line_ids': fields.one2many(
            'cleanup.purge.line.data',
            'wizard_id', 'Data to purge'),
        }
