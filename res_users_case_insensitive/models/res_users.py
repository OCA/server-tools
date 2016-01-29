# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2016-TODAY LasLabs, Inc. [https://laslabs.com]
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

from openerp import models, api, fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    login = fields.Char(
        'Login',
        size=64,
        required=True,
        help='Used to log into the system. Case insensitive.',
    )

    @api.model
    def search(self, domain, *args, **kwargs):
        '''
        Overload search to lowercase name domains. Can't do in a typical
        search method due to the field not being computed
        '''
        for idx, _domain in enumerate(domain):
            if _domain[0] == 'login':
                lower = _domain[2].lower() if _domain[2] else False
                domain[idx] = (_domain[0], _domain[1], lower)
        return super(ResUsers, self).search(domain, *args, **kwargs)

    @api.model
    def create(self, vals, ):
        ''' Overload create to lowercase login '''
        vals['login'] = vals.get('login', '').lower()
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals, ):
        ''' Overload write to lowercase login '''
        if vals.get('login'):
            vals['login'] = vals['login'].lower()
        return super(ResUsers, self).write(vals)
