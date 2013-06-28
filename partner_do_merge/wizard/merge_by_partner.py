# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

class wizard_merge_partner_by_partner(osv.osv_memory):
    _name = 'wizard.merge.partner.by.partner'
    
    def default_get(self, cr, uid, fields, context=None):
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, context.get('active_id'),\
            context=context)
        res = {'partner_id' : partner.id , 'partner_ids' : [partner.id]}
        return res
    
    _columns = {
        'partner_id' : fields.many2one('res.partner', 'Partner', readonly=True,
            required=True, help='Correct partner to complete data'),
        'partner_ids': fields.many2many('res.partner', 'partners_to_merge',
            'partner_id', 'wizard_id', 'Partner to merge', help='Partners to '\
            'merge'),
    }
        
    def merge_cb(self, cr, uid, ids, context=None):
        base_partner_obj = self.pool.get('base.partner.merge.automatic.wizard')
        partner_obj = self.pool.get('res.partner')
        for data in self.browse(cr, uid, ids, context=context):
            dst_partner = data.partner_id
            partner_ids = set(map(int, data.partner_ids))
            if len(partner_ids) >= 2:
                base_partner_obj.merge_pbp(cr, SUPERUSER_ID, partner_ids,\
                dst_partner, context=context)
            adminpac_ids = {}
            for partner in data.partner_ids:
                if partner.adminpaq_id:
                    adminpac_ids.update({partner.id : partner.adminpaq_id})
            if len(adminpac_ids) == 1:
                partner_obj.write(cr, uid, adminpac_ids.keys()[0], {
                    'adminpaq_id' : 0})
                partner_obj.write(cr, uid, data.partner_id.id, {
                    'adminpaq_id' : adminpac_ids.values()[0]})
        return True
    
    
