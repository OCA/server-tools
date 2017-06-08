# -*- coding: utf-8 -*-
##############################################################################
#
#    BizzAppDev
#    Copyright (C) 2004-TODAY bizzappdev(<http://www.bizzappdev.com>).
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
from openerp.tools import config


class project_configuration(osv.TransientModel):
    _inherit = 'base.config.settings'

    _columns = {
        'test': fields.boolean('Active Test Mode'),

        'develop': fields.boolean('Active Develop Mode'),
    }

    def get_default_test(self, cr, uid, ids, context=None):

        test = config.get('test', {}).get(cr.dbname, False)

        return {'test': test or False}

    def get_default_develop(self, cr, uid, ids, context=None):

        develop = config.get('develop', {}).get(cr.dbname, False)

        return {'develop': develop or False}

    def set_develop(self, cr, uid, ids, context=None):
        if not config.get('develop'):
            config['develop'] = {}

        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config['develop'][cr.dbname] = record.develop
            config_parameters.set_param(
                cr, uid, "develop", record.develop or '',
                context=context)

    def set_test(self, cr, uid, ids, context=None):
        if not config.get('test'):
            config['test'] = {}

        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config['test'][cr.dbname] = record.test
            config_parameters.set_param(
                cr, uid, "test", record.test or '',
                context=context)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
