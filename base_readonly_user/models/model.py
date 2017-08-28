# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from openerp.osv import orm
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class IrModel(orm.Model):
    _inherit = 'ir.model'

    def _register_hook(self, cr):
        ids = self.search(cr, SUPERUSER_ID, [])
        for model in self.browse(cr, SUPERUSER_ID, ids):
            model_name = model.model
            model_obj = self.pool.get(model_name)
            if model_obj:
                model_obj.create = self._wrap_create(model_obj.create)
                model_obj.write = self._wrap_write(model_obj.write)
                model_obj.unlink = self._wrap_unlink(model_obj.unlink)
        return super(IrModel, self)._register_hook(cr)

    def create(self, cr, uid, vals, context=None):
        res_id = super(IrModel, self).create(cr, uid, vals, context=context)
        self._register_hook(cr)
        return res_id

    def _wrap_create(self, old_create):
        def wrapper(cr, uid, vals, context=None, **kwargs):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            if user.readonly_user:
                raise orm.except_orm(
                    _('Error'),
                    _("Readonly user can't create records"))
            else:
                return old_create(cr, uid, vals, context=context, **kwargs)
        return wrapper

    def _wrap_write(self, old_write):
        def wrapper(cr, uid, ids, vals, context=None, **kwargs):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            if user.readonly_user:
                raise orm.except_orm(
                    _('Error'),
                    _("Readonly user can't write records"))
            else:
                return old_write(cr, uid, ids, vals, context=context, **kwargs)
        return wrapper

    def _wrap_unlink(self, old_unlink):
        def wrapper(cr, uid, ids, context=None, **kwargs):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            if user.readonly_user:
                raise orm.except_orm(
                    _('Error'),
                    _("Readonly user can't delete records"))
            else:
                return old_unlink(cr, uid, ids, context=context, **kwargs)
        return wrapper
