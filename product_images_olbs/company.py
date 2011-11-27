# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author Nicolas Bessi & Guewen Baconnier. Copyright Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _

class ResCompany(osv.osv):
    """Override company to add images configuration"""
    _inherit = "res.company"
    _columns = {        
        'local_media_repository':fields.char(
                        'Images Repository Path', 
                        size=256, 
                        required=True,
                        help='Local mounted path on OpenERP server where all your images are stored.'
                    ),
    }    
    
    def get_local_media_repository(self, cr, uid, id=None, context=None):
        if id:
            return self.browse(cr, uid, id, context=context).local_media_repository
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.local_media_repository

ResCompany()
