# -*- coding: utf-8 -*-
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

from openerp.osv import orm


class ir_import(orm.TransientModel):
    _inherit = 'base_import.import'

    def do(self, cr, uid, id, fields, options, dryrun=False, context=None):
        """When importing large amounts of data, the parent store
        computation can have major negative performance issues.

        Deferring the parent store computation to the end of the import
        can speed long imports tremendously.
        """

        defer = options.get('defer')

        if defer:
            context['defer_parent_store_computation'] = True

        res = super(ir_import, self).do(
            cr, uid, id, fields, options, dryrun, context=context
        )

        if not dryrun and defer:
            record = self.browse(cr, uid, id, context=context)
            self.pool[record.res_model]._parent_store_compute(cr)

        return res
