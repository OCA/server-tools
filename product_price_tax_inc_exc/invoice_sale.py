# -*- encoding: utf-8 -*-
###############################################################################
#
#   product_price_tax_inc_exc for OpenERP
#   Copyright (C) 2011-TODAY Akretion <http://www.akretion.com>. All Rights Reserved
#     @author Sébastien BEAU <sebastien.beau@akretion.com>
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from tools.translate import _
from openerp.osv.orm import Model, AbstractModel

class InvoiceSale(Model):
    _register = False

    def _need_to_update_line(self, cr, uid, change_done, lines, context=None):
        if lines:
            return {'warning': {
                        'title': _('Warning !'),
                        'message' :  _("The %s have change please update the"
                        "order line manually"%change_done)
                    }}
        else:
            return {}

    def fiscal_position_id_change(self, cr, uid, ids, fiscal_position_id, tax_inc, lines, context=None):
        res={}
        if fiscal_position_id:
            fiscal_obj = self.pool.get('account.fiscal.position')
            fiscal = fiscal_obj.browse(cr, uid, fiscal_position_id)
            res = self._need_to_update_line(cr, uid, 'fiscal position', lines, context=context)
            if fiscal.price_compatibility == 'tax-exc':
                res.update({'value': {'tax_inc' : False}})
            elif fiscal.price_compatibility == 'tax-inc':
                res.update({'value': {'tax_inc' : True}})
        else:
            res.update({'value':{
                'tax_inc': self.default_get(cr, uid, ['tax_inc'], context=context).get('tax_inc', False)
                }})
        return res

    def tax_inc_change(self, cr, uid, ids, fiscal_position_id, tax_inc, lines, context=None):
        res = self._need_to_update_line(cr, uid, 'tax included', lines, context=context)
        if fiscal_position_id:
            fiscal_obj = self.pool.get('account.fiscal.position')
            fiscal = fiscal_obj.browse(cr, uid, fiscal_position_id)
            warning_mode = False
            if fiscal.price_compatibility == 'tax-exc' and tax_inc:
                warning_mode = "include"
            elif fiscal.price_compatibility == 'tax-inc' and not tax_inc:
                warning_mode = "exclude"
            if warning_mode:
                res = {
                    'value' : {'tax_inc': not tax_inc},
                    'warning': {
                        'title': _('User Error !'),
                        'message' :  _("The fiscal position selected "
                            "is incompatible with the mode tax %s"%warning_mode)
                    }
                }
        return res

class InvoiceSaleLine(Model):
    _register = False

    def product_id_change(self, cr, uid, ids, *args, **kwargs):
        res = super(InvoiceSaleLine, self).product_id_change(cr, uid, ids, *args, **kwargs)

        # UGLY OpenERP API :'(, context can be in the **kwargs or *args
        if 'context' in kwargs:
            context = kwargs['context']
        else:
            context=None
            for arg in args: #search the context :S
                if isinstance(arg, dict) and 'lang' in arg:
                    context = arg
                    break
        tax_keys = {
            'account.invoice.line': 'invoice_line_tax_id',
            'sale.order.line': 'tax_id',
            }
        tax_ids = res.get('value', {}).get(tax_keys[self._name])
        if context and context.get('tax_inc') and tax_ids:
            new_tax_ids = []
            for tax in self.pool.get('account.tax').browse(cr, uid, tax_ids, context=context):
                new_tax_ids.append(tax.related_inc_tax_id.id or tax.id)
            res['value'][tax_keys[self._name]] = new_tax_ids
        return res

