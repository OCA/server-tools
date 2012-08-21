# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
#   product_custom_attributes for OpenERP                                      #
#   Copyright (C) 2011 Akretion Benoît GUILLOT <benoit.guillot@akretion.com>  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv.orm import Model
from openerp.osv import fields
from openerp.osv.osv import except_osv
from lxml import etree
from tools.translate import _

class product_template(Model):

    _inherit = "product.template"

    _columns = {
        'attribute_custom_tmpl': fields.serialized('Custom Template Attributes'),
    }

class product_product(Model):

    _inherit = "product.product"

    _columns = {
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'attribute_custom_variant': fields.serialized('Custom Variant Attributes'),
    }


    def open_attributes(self, cr, uid, ids, context=None):
        ir_model_data_obj = self.pool.get('ir.model.data')
        ir_model_data_id = ir_model_data_obj.search(cr, uid, [['model', '=', 'ir.ui.view'], ['name', '=', 'product_attributes_form_view']], context=context)
        if ir_model_data_id:
            res_id = ir_model_data_obj.read(cr, uid, ir_model_data_id, fields=['res_id'])[0]['res_id']
        set_id = self.read(cr, uid, ids, fields=['attribute_set_id'], context=context)[0]['attribute_set_id']

        if not set_id:
            raise except_osv(_('User Error'), _('Please choose an attribute set before opening the product attributes'))

        return {
            'name': 'Product Attributes',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': self._name,
            'context': "{'set_id': %s, 'open_attributes': %s}"%(set_id[0], True),
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'res_id': ids and ids[0] or False,
        }

    def save_and_close_product_attributes(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def _build_attribute_field(self, cr, uid, page, attribute, context=None):
        parent = page
        kwargs = {'name': "%s" % attribute.name}
        if attribute.ttype == 'many2many':
            parent = etree.SubElement(page, 'group', colspan="2", col="4")
            sep = etree.SubElement(parent, 'separator',
                                    string="%s" % attribute.field_description, colspan="4")
            kwargs['nolabel'] = "1"
        if attribute.ttype in ['many2one', 'many2many']:
            kwargs['domain'] = "[('attribute_id', '=', %s)]" % attribute.attribute_id.id
        field = etree.SubElement(parent, 'field', **kwargs)
        return parent

    def _build_attributes_notebook(self, cr, uid, set_id, context=None):
        attribute_set = self.pool.get('attribute.set').browse(cr, uid, set_id, context=context)
        notebook = etree.Element('notebook', name="attributes_notebook", colspan="4")
        toupdate_fields = []
        for group in attribute_set.attribute_group_ids:
            page = etree.SubElement(notebook, 'page', string=group.name.capitalize())
            for attribute in group.attribute_ids:
                toupdate_fields.append(attribute.name)
                self._build_attribute_field(cr, uid, page, attribute, context=context)
        return notebook, toupdate_fields

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(product_product, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and context.get('set_id'):
            eview = etree.fromstring(result['arch'])
            #hide button under the name
            button = eview.xpath("//button[@name='open_attributes']")
            if button:
                button = button[0]
                button.getparent().remove(button)
            attributes_notebook, toupdate_fields = self._build_attributes_notebook(cr, uid, context['set_id'], context=context)
            result['fields'].update(self.fields_get(cr, uid, toupdate_fields, context))
            if context.get('open_attributes'):
                placeholder = eview.xpath("//separator[@string='attributes_placeholder']")[0]
                placeholder.getparent().replace(placeholder, attributes_notebook)
            elif context.get('open_product_by_attribute_set'):
                main_page = etree.Element('page', string=_('Custom Attributes'))
                main_page.append(attributes_notebook)
                info_page = eview.xpath("//page[@string='Information']")[0]
                info_page.addnext(main_page)
            result['arch'] = etree.tostring(eview, pretty_print=True)
        return result
