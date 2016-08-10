# -*- coding: utf-8 -*-
# Copyright 2016 - Ursa Information Systems <http://ursainfosystems.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from openerp import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.v7
    def get_export_models(self, cr, uid):
        return self.fetch_export_models(cr, uid)
    
    @api.v8
    def get_export_models(self):
        uid = self.id or self.env.uid
        return self.fetch_export_models(self.env.cr, uid)
    
    def fetch_export_models(self, cr, uid):
        groups_id = [group.id for group in self.browse(cr, uid, uid).groups_id]
        accessobj = self.pool['ir.model.access']
        accessobj_ids = accessobj.search(cr, uid, [('perm_export','=',True),('group_id','in',groups_id)])
        model_names = [access_obj.model_id.model for access_obj in accessobj.browse(cr, uid, accessobj_ids)]
        #make distinct value in list
        model_names = list(set(model_names))
        return model_names