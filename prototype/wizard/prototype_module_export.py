# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
from openerp.osv import fields,osv
from openerp.tools.translate import _


class prototype_module_export(osv.osv_memory):
    _name = "prototype.module.export"

    _columns = {
        'name': fields.char('File Name', readonly=True),
        'api_version': fields.selection([('8.0','8.0'),
                                         ('7.0', '7.0')], 'API version',
                                         required=True),
        'data': fields.binary('File', readonly=True),
        'state': fields.selection([('choose', 'choose'),   #  choose version
                                   ('get', 'get')])        #  get module
    }
    _defaults = {
        'state': 'choose',
        'api_version': '8.0',
    }

    def act_getfile(self, cr, uid, ids, context=None):
        """
        Export a zip file containing the module based on the information
        provided in the prototype, using the templates chosen in the wizard.
        """
        this = self.browse(cr, uid, ids)[0]

        # TODO: Implement the export logic here
        filename = 'new'
        this.name = "%s.%s" % (filename, 'zip')
        out = 'toto'
        # /TODO

        self.write(cr, uid, ids, {'state': 'get',
                                  'data': out,
                                  'name':this.name}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'prototype.module.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
