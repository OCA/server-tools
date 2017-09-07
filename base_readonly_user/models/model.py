# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# Copyright 2017 Alex Comba - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

from openerp.osv import orm
from openerp import SUPERUSER_ID, _


class IrModel(orm.Model):
    _inherit = 'ir.model'

    def _patch_readonly_user(self, cr, ids):

        def make_create():
            def create(self, cr, uid, vals, context=None, **kwargs):
                user = self.pool['res.users'].browse(
                    cr, uid, uid, context=context)
                if user.readonly_user:
                    raise orm.except_orm(
                        _('Error'),
                        _("Readonly user can't create records"))
                else:
                    return create.origin(
                        self, cr, uid, vals, context=context, **kwargs)
            return create

        def make_write():
            def write(self, cr, uid, ids, vals, context=None, **kwargs):
                user = self.pool['res.users'].browse(
                    cr, uid, uid, context=context)
                if user.readonly_user:
                    raise orm.except_orm(
                        _('Error'),
                        _("Readonly user can't write records"))
                else:
                    return write.origin(
                        self, cr, uid, ids, vals, context=context, **kwargs)
            return write

        def make_unlink():
            def unlink(self, cr, uid, ids, context=None, **kwargs):
                user = self.pool['res.users'].browse(
                    cr, uid, uid, context=context)
                if user.readonly_user:
                    raise orm.except_orm(
                        _('Error'),
                        _("Readonly user can't unlink records"))
                else:
                    return unlink.origin(
                        self, cr, uid, ids, context=context, **kwargs)
            return unlink

        for model in self.browse(cr, SUPERUSER_ID, ids):
            Model = self.pool.get(model.model)
            if Model:
                Model._patch_method('create', make_create())
                Model._patch_method('write', make_write())
                Model._patch_method('unlink', make_unlink())
        return super(IrModel, self)._register_hook(cr)

    def _register_hook(self, cr):
        self._patch_readonly_user(cr, self.search(cr, SUPERUSER_ID, []))
        return super(IrModel, self)._register_hook(cr)

    def create(self, cr, uid, vals, context=None):
        res_id = super(IrModel, self).create(cr, uid, vals, context=context)
        self._patch_readonly_user(cr, [res_id])
        return res_id
