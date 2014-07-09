# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    product_multi_price for OpenERP                                          #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>   #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from openerp.osv.orm import Model, setup_modifiers
from openerp.osv.osv import except_osv
from lxml import etree
from tools.translate import _



class product_product(Model):
    _inherit = "product.product"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(product_product, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type=='form' and result.get('model') == 'product.product' and '<field name="list_price" modifiers="{}"/>' in result['arch']:
            product_price_fields_obj = self.pool.get('product.price.fields')
            product_price_fields_ids = product_price_fields_obj.search(cr, uid, [], context=context)
            price_fields = []
            tax_inc = False
            tax_ex = False
#            arch_1 = u"""<group colspan="2" col="10">\n<separator string="Tax exclude prices" colspan="10"/>\n"""
#            arch_2 = u"""</group>\n"""
#            arch_3 = u"""<group colspan="2" col="10">\n<separator string="Tax include prices" colspan="10"/>\n"""
#            arch_4 = u"""<separator colspan="10"/>\n</group>"""
#            for field in product_price_fields_obj.browse(cr, uid, product_price_fields_ids, context=context):
#                price_fields += [field.field_name, field.basedon_field_id.name, field.product_coef_field_id.name]
#                fields_arch = u"""<label string="%s :" colspan="3"/>\n<field name="%s" colspan="4" nolabel="1"/>\n<field name="%s" string="Coef" colspan="1" attrs="{'readonly':[('%s','!=','product_coef')]}" modifiers="{&quot;readonly&quot;:[[&quot;%s&quot;,&quot;!=&quot;,&quot;product_coef&quot;]]}"/>\n<field name="%s" colspan="1" nolabel="1" attrs="{'readonly':[('%s','!=','manual')]}" modifiers="{&quot;readonly&quot;:[[&quot;%s&quot;,&quot;!=&quot;,&quot;manual&quot;]]}"/>\n""" % (field.name, field.basedon_field_id.name, field.product_coef_field_id.name, field.basedon_field_id.name, field.basedon_field_id.name, field.field_name, field.basedon_field_id.name, field.basedon_field_id.name)
#                if field.tax_included:
#                    arch_3 +=  fields_arch
#                    tax_inc = True
#                else:
#                    arch_1 += fields_arch
#                    tax_ex = True
#                print price_fields
#            #remove group tax include or tax exclude if no price in it
#            if not tax_inc:
#                arch = arch_1 + arch_4
#            elif not tax_ex:
#                arch = arch_3 + arch_4
#            else:
#                arch = arch_1 + arch_2 + arch_3 + arch_4
#            import pdb;pdb.set_trace()
#            result['fields'].update(self.fields_get(cr, uid, price_fields, context))
#            result['arch'] = result['arch'].decode('utf8').replace('<field name="list_price" modifiers="{}"/>', arch)
##            print result
            eview = etree.fromstring(result['arch'])
            #select separator just before field : list_price in order to remove it
            main_sep = eview.xpath("//field[@name='list_price']/preceding-sibling::*[1]")
            main_sep = main_sep[0]
            main_sep.getparent().remove(main_sep)
            btn = eview.xpath("//field[@name='list_price']")
            if btn:
                btn = btn[0]
                group_ex = etree.Element('group', colspan="2", col="11")
                _separator_ex = etree.SubElement(
                                group_ex,
                                'separator',
                                colspan="10",
                                string="Tax exclude prices")
                group_inc = etree.Element('group', colspan="2", col="11")
                _separator_inc = etree.SubElement(
                                group_inc,
                                'separator',
                                colspan="10",
                                string="Tax include prices")
                group_sep = etree.Element('group', colspan="2", col="11")
                _separator_end = etree.SubElement(
                                group_sep,
                                'separator',
                                colspan="11")
                inc_price = self.pool.get('product.price.fields').search(cr, uid, [
                                                                        ('tax_included', '=', True)
                                                                        ], context=context)
                if inc_price:
                    button_parent = group_inc
                else:
                    button_parent = group_ex
                _button = etree.SubElement(
                                button_parent,
                                'button',
                                colspan="1",
                                name="refresh_prices",
                                string="Refresh Prices",
                                type="object")
                for field in product_price_fields_obj.browse(cr, uid, product_price_fields_ids, context=context):
                    price_fields = [field.field_name, field.basedon_field_id.name, field.product_coef_field_id.name, field.inc_price_field_id.name]
                    result['fields'].update(self.fields_get(cr, uid, price_fields, context))
                    if field.tax_included:
                        parent =  group_inc
                        tax_inc = True
                        inc_readonly = "0"
                        ex_readonly = "1"
                    else:
                        parent = group_ex
                        tax_ex = True
                        inc_readonly = "1"
                        ex_readonly = "0"
                    _label = etree.SubElement(
                                parent,
                                'label',
                                colspan="3",
                                string="%s" % field.name)
                    _basedon = etree.SubElement(
                                parent,
                                'field',
                                name="%s" % field.basedon_field_id.name,
                                colspan="4",
                                nolabel="1")
                    setup_modifiers(
                        _basedon, field=result['fields'][field.basedon_field_id.name], context=context)
                    coef = etree.SubElement(
                                parent,
                                'field',
                                digits="(18, 6)",
                                name="%s" % field.product_coef_field_id.name,
                                string="Coef",
                                colspan="1",
                                attrs="{'readonly':[('%s','!=','product_coef')]}" % field.basedon_field_id.name)
                    setup_modifiers(coef,
                                    field=result['fields'][field.product_coef_field_id.name],
                                    context=context)
                    price = etree.SubElement(
                                parent,
                                'field',
                                digits ="(12, %s)" % (self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price')),
                                name="%s" % field.field_name,
                                colspan="1",
                                nolabel="1",
                                readonly = ex_readonly,
                                attrs="{'readonly':[('%s','!=','manual')]}" % field.basedon_field_id.name)
                    setup_modifiers(price,
                                    field=result['fields'][field.field_name],
                                    context=context)
                    inc_price = etree.SubElement(
                                parent,
                                'field',
                                digits ="(12, %s)" % (self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price')),
                                name="%s" % field.inc_price_field_id.name,
                                colspan="1",
                                nolabel="1",
                                readonly = inc_readonly,
                                attrs="{'readonly':[('%s','!=','manual')]}" % field.basedon_field_id.name)
                    setup_modifiers(inc_price,
                                    field=result['fields'][field.inc_price_field_id.name],
                                    context=context)
                arch = etree.Element('group', colspan="2", col="11")
                if tax_inc:
                    arch.extend(group_inc)
                if tax_ex:
                    arch.extend(group_ex)
                arch.extend(group_sep)
                btn.getparent().replace(btn, arch)
            result['arch'] = etree.tostring(eview, pretty_print=True)
        return result

    def default_get(self, cr, uid, fields_list, context=None):
        defaults = super(product_product, self).default_get(cr, uid, fields_list, context=context)
        product_price_fields_obj = self.pool.get('product.price.fields')
        product_price_fields_ids = product_price_fields_obj.search(cr, uid, [], context=context)
        for field in product_price_fields_obj.browse(cr, uid, product_price_fields_ids, context=context):
            if not defaults.get(field.basedon_field_id.name):
                if field.default_basedon:
                    defaults[field.basedon_field_id.name] = field.default_basedon
        return defaults

    def refresh_prices(self, cr, uid, ids, context=None):
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if context is None: context={}
        context['simple_read'] = True
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context={}
        read = False
        if not fields:
            fields = []
        for field in fields:
            if field[0:5] == 'x_pm_':
                read = True
                break
        if read and not context.get('simple_read'):
            tax_obj = self.pool.get('account.tax')
            prod_price_fields_obj = self.pool.get('product.price.fields')
            add_fields = []
            if not 'categ_id' in fields:
                fields.append('categ_id')
                add_fields.append('categ_id')
            if not 'standard_price' in fields:
                fields.append('standard_price')
                add_fields.append('standard_price')
            if not 'taxes_id' in fields:
                fields.append('taxes_id')
                add_fields.append('taxes_id')
            for field in fields:
                name = False
                if field[0:11] == 'x_pm_price_':
                    name = field[11:]
                    if not 'x_pm_product_coef_' + name in fields:
                        fields.append('x_pm_product_coef_' + name)
                        add_fields.append('x_pm_product_coef_' + name)
                    if not 'x_pm_inc_price_' + name in fields:
                        fields.append('x_pm_inc_price_' + name)
                        add_fields.append('x_pm_inc_price_' + name)
                elif field[0:18] == 'x_pm_product_coef_':
                    name = field[18:]
                    if name == 'list_price':
                        if not name in fields:
                            fields.append(name)
                            add_fields.append(name)
                    elif not 'x_pm_price_' + name in fields:
                        fields.append('x_pm_price_' + name)
                        add_fields.append('x_pm_price_' + name)
                    if not 'x_pm_inc_price_' + name in fields:
                        fields.append('x_pm_inc_price_' + name)
                        add_fields.append('x_pm_inc_price_' + name)
                elif field[0:15] == 'x_pm_inc_price_':
                    name = field[15:]
                    if name == 'list_price':
                        if not name in fields:
                            fields.append(name)
                            add_fields.append(name)
                    elif not 'x_pm_price_' + name in fields:
                        fields.append('x_pm_price_' + name)
                        add_fields.append('x_pm_price_' + name)
                    if not 'x_pm_product_coef_' + name in fields:
                        fields.append('x_pm_product_coef_' + name)
                        add_fields.append('x_pm_product_coef_' + name)
                if name:
                    if not 'x_pm_basedon_' + name in fields:
                        fields.append('x_pm_basedon_' + name)
                        add_fields.append('x_pm_basedon_' + name)
            results = super(product_product, self).read(cr, uid, ids, fields=fields, context=context, load=load)
            to_unlist = False
            if not hasattr(results, "__iter__"):
                results = results
                to_unlist = True
            for result in results:
                fields = list(set(fields)-set(add_fields))
                for field in fields:
                    name = False
                    if field[0:11] == 'x_pm_price_':
                        name = field[11:]
                    elif field[0:18] == 'x_pm_product_coef_':
                        name = field[18:]
                    elif field[0:15] == 'x_pm_inc_price_':
                        name = field[15:]
                    if name:
                        if name == 'list_price':
                            price_name = 'list_price'
                        else:
                            price_name = 'x_pm_price_' + name
                        tax_inc = False
                        price_field_ids = prod_price_fields_obj.search(cr, uid, [
                                                                ('field_name', '=', price_name)
                                                                ], context=context)
                        if price_field_ids:
                            price_field = prod_price_fields_obj.read(cr, uid, price_field_ids[0], ['tax_included'], context=context)
                            if price_field.get('tax_included'):
                                tax_inc = True
                        if result.get('taxes_id'):
                            #TODO support several taxes ?
                            tax = tax_obj.browse(cr, uid, result['taxes_id'][0], context=context)
                        if result['x_pm_basedon_' + name] == 'manual':
                            if result['standard_price']:
                                if tax_inc and result.get('taxes_id'):
                                    if not tax.related_inc_tax_id:
                                        raise except_osv(_("No related tax"), _("You need to define a related included tax for the sale tax!"))
                                    taxes = tax_obj.compute_all_with_precision(cr, uid, [tax.related_inc_tax_id], result['x_pm_inc_price_' + name], 1, precision=6)
                                    result[price_name] = taxes['total']
                                elif result.get('taxes_id'):
                                    taxes = tax_obj.compute_all_with_precision(cr, uid, [tax], result[price_name], 1, precision=6)
                                    result['x_pm_inc_price_' + name] = taxes['total_included']
                                else:
                                    result['x_pm_inc_price_' + name] = result[price_name]
                                result['x_pm_product_coef_' + name] = result[price_name]/result['standard_price']
                            else:
                                result['x_pm_product_coef_' + name] = 0
                        elif result['x_pm_basedon_' + name] == 'product_coef':
                            if result.get('x_pm_product_coef_' + name):
                                price_ex = result['standard_price']*result['x_pm_product_coef_' + name]
                            else:
                                price_ex = result['standard_price']
                        elif result['x_pm_basedon_' + name] == 'categ_coef':
                            if isinstance(result['categ_id'], (int, long)):
                                categ_id = result['categ_id']
                            else:
                                categ_id = result['categ_id'][0]
                            categ = self.pool.get('product.category').read(cr, uid, [categ_id], ['x_pm_categ_coef_' + name], context=context)
                            if categ[0].get('x_pm_categ_coef_' + name):
                                result['x_pm_product_coef_' + name] = categ[0]['x_pm_categ_coef_' + name]
                            else:
                                result['x_pm_product_coef_' + name] = 1
                            price_ex = result['standard_price']*result['x_pm_product_coef_' + name]
                        if result['x_pm_basedon_' + name] in ['categ_coef', 'product_coef']:
                            if result.get('taxes_id'):
                                taxes = tax_obj.compute_all_with_precision(cr, uid, [tax], price_ex, 1, precision=6)
                                result['x_pm_inc_price_' + name] = taxes['total_included']
                            else:
                                result['x_pm_inc_price_' + name] = price_ex
                            result[price_name] = price_ex
                for field in add_fields:
                    if result.get(field):
                        del result[field]
            if to_unlist:
                results = results[0]
        else:
            results = super(product_product, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        return results



class product_category(Model):
    _inherit = 'product.category'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(product_category, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type=='form':
            product_price_fields_obj = self.pool.get('product.price.fields')
            product_price_fields_ids = product_price_fields_obj.search(cr, uid, [], context=context)
            price_fields = []
            eview = etree.fromstring(result['arch'])
            btn = eview.xpath("//field[@name='type']")
            if btn:
                btn = btn[0]
                arch = etree.Element('group', colspan="2", col="2")
                _separator = etree.SubElement(
                                arch,
                                'separator',
                                colspan="2",
                                string="Product price coefficients")
                for field in product_price_fields_obj.browse(cr, uid, product_price_fields_ids, context=context):
                    price_fields.append(field.categ_coef_field_id.name)
                    _coef = etree.SubElement(
                                arch,
                                'field',
                                digits="(18, 6)",
                                name="%s" % field.categ_coef_field_id.name,
                                string="%s" % field.name,
                                colspan="2")
                btn.getparent().append(arch)
            result['fields'].update(self.fields_get(cr, uid, price_fields, context))
            result['arch'] = etree.tostring(eview, pretty_print=True)
        return result
