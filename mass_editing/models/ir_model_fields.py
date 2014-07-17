# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
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

from openerp.osv import orm


class IrModelFields(orm.Model):
    _inherit = 'ir.model.fields'

    def search(
            self, cr, uid, args, offset=0, limit=0, order=None, context=None,
            count=False):
        model_domain = []
        for domain in args:
            if (len(domain) > 2 and domain[0] == 'model_id'
                    and isinstance(domain[2], basestring)):
                model_domain += [
                    ('model_id', 'in', map(int, domain[2][1:-1].split(',')))
                ]
            else:
                model_domain.append(domain)
        return super(IrModelFields, self).search(
            cr, uid, model_domain, offset=offset, limit=limit, order=order,
            context=context, count=count
        )
