# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi. Copyright Camptocamp SA
##############################################################################
from osv import fields, models

class IrModelAccess(models.Model):
    "We inherit ir model access to add specific write unlink and copy behavior"
    _name = 'ir.model.access'
    _inherit = "ir.model.access"
                    
    def _acces_can_be_modified(self, cr, uid, context=None):
        context = context or {}
        on = self.pool.get('ir.config_parameter').get_param(cr, uid, 'protect_security?', default=False, context=context)
        if on in (1, "1", "YES", True):
            if context.get('manual_security_override', False):
                return True
            return False
            
        else:
            return True
        
    def write(self, cr, uid, ids, vals, context=None):
        res =True
        context = context or {}
        if self._acces_can_be_modified(cr, uid, context=context):
            res = super(IrModelAccess, self).write(cr, uid, ids, vals, context=context)
        return res


    def unlink(self, cr, uid, ids, context=None):
        res = True
        context = context or {}
        # I'm note sur about this one maybe we should do nothing
        if self._acces_can_be_modified(cr, uid, context=context): 
            vals = {'perm_read':False,
             'perm_write': False, 
             'perm_unlink': False,
             'perm_create': False}
            super(IrModelAccess, self).write(cr, uid, ids, vals, context=context)
        else: 
            res = super(IrModelAccess, self).unlink(cr, uid, ids, context=context)

        return res
        
IrModelAccess()