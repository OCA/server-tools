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
from openerp.addons.base.ir.ir_model import MODULE_UNINSTALL_FLAG


class IrModel(orm.Model):
    _inherit = 'ir.model'

    def _drop_table(self, cr, uid, ids, context=None):
        # Allow to skip this step during model unlink
        # The super method crashes if the model cannot be instantiated
        if context and context.get('no_drop_table'):
            return True
        return super(IrModel, self)._drop_table(cr, uid, ids, context=context)


class CleanupPurgeLineModel(orm.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.model'

    _columns = {
        'wizard_id': fields.many2one(
            'cleanup.purge.wizard.model', 'Purge Wizard', readonly=True),
        }

    def purge(self, cr, uid, ids, context=None):
        """
        Unlink models upon manual confirmation.
        """
        model_pool = self.pool['ir.model']
        attachment_pool = self.pool['ir.attachment']
        constraint_pool = self.pool['ir.model.constraint']
        fields_pool = self.pool['ir.model.fields']

        local_context = (context or {}).copy()
        local_context.update({
            MODULE_UNINSTALL_FLAG: True,
            'no_drop_table': True,
            })

        for line in self.browse(cr, uid, ids, context=context):
            cr.execute(
                "SELECT id, model from ir_model WHERE model = %s",
                (line.name,))
            row = cr.fetchone()
            if row:
                self.logger.info('Purging model %s', row[1])
                attachment_ids = attachment_pool.search(
                    cr, uid, [('res_model', '=', line.name)], context=context)
                if attachment_ids:
                    cr.execute(
                        "UPDATE ir_attachment SET res_model = FALSE "
                        "WHERE id in %s",
                        (tuple(attachment_ids), ))
                constraint_ids = constraint_pool.search(
                    cr, uid, [('model', '=', line.name)], context=context)
                if constraint_ids:
                    constraint_pool.unlink(
                        cr, uid, constraint_ids, context=context)
                relation_ids = fields_pool.search(
                    cr, uid, [('relation', '=', row[1])], context=context)
                for relation in relation_ids:
                    try:
                        # Fails if the model on the target side
                        # cannot be instantiated
                        fields_pool.unlink(cr, uid, [relation],
                                           context=local_context)
                    except AttributeError:
                        pass
                model_pool.unlink(cr, uid, [row[0]], context=local_context)
                line.write({'purged': True})
                cr.commit()
        return True


class CleanupPurgeWizardModel(orm.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.model'

    def default_get(self, cr, uid, fields, context=None):
        res = super(CleanupPurgeWizardModel, self).default_get(
            cr, uid, fields, context=context)
        if 'name' in fields:
            res['name'] = _('Purge models')
        return res

    def find(self, cr, uid, context=None):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        cr.execute("SELECT model from ir_model")
        for (model,) in cr.fetchall():
            if not self.pool.get(model):
                res.append((0, 0, {'name': model}))
        if not res:
            raise orm.except_orm(
                _('Nothing to do'),
                _('No orphaned models found'))
        return res

    _columns = {
        'purge_line_ids': fields.one2many(
            'cleanup.purge.line.model',
            'wizard_id', 'Models to purge'),
        }
