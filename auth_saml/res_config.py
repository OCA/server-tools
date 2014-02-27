# -*- coding: utf-8 -*-
##############################################################################
#
#    XCG Consulting Group
#    Copyright (C) 2010-2014 XCG Consulting s.a.s
#    <http://www.xcg-consulting.fr.
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import osv, fields

#import logging
#_logger = logging.getLogger(__name__)


class base_config_settings(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'auth_saml_local_enabled': fields.boolean(
            'Allow users to sign in with a Local Authentic'
        ),
    }

    def get_saml_providers(self, cr, uid, fields, context=None):
        local_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'auth_saml', 'provider_local'
        )[1]

        rl = self.pool.get('auth.saml.provider').read(
            cr, uid, [local_id], ['enabled'], context=context
        )

        return {
            'auth_saml_local_enabled': rl[0]['enabled'],
        }

    def set_saml_providers(self, cr, uid, ids, context=None):
        local_id = self.pool.get('ir.model.data').get_object_reference(
            cr, uid, 'auth_saml', 'provider_local'
        )[1]

        config = self.browse(cr, uid, ids[0], context=context)

        rl = {
            'enabled': config.auth_saml_local_enabled,
        }

        self.pool.get('auth.saml.provider').write(cr, uid, [local_id], rl)
