# -*- coding: utf-8 -*-
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

from openerp.osv import orm, fields


class ResCompany(orm.Model):
    """Override company to add images configuration"""
    _inherit = "res.company"
    _columns = {
        'local_media_repository': fields.char(
            'Images Repository Path',
            help='Local directory on the OpenERP server '
                 'where all images are stored.'),
        }

    def get_local_media_repository(self, cr, uid, id=None, context=None):
        if isinstance(id, (tuple, list)):
            assert len(id) == 1, "One ID expected"
            id = id[0]
        if id:
            return self.browse(cr, uid, id, context=context).local_media_repository
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.local_media_repository
