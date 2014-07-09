# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   Inspired by the module product_custom_attributes                          #
#   by Benoît GUILLOT <benoit.guillot@akretion.com>, Akretion                 #
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
from tools.translate import translate
from lxml import etree


class stock_production_lot(Model):
    _inherit = "stock.production.lot"

    _columns = {
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
        'attribute_group_ids': fields.related(
            'attribute_set_id',
            'attribute_group_ids',
            type='many2many',
            relation='attribute.group'
            )
    }

    def open_attributes(self, cr, uid, ids, context=None):
        """Open the attributes of an object

        This method is called when the user presses the Open Attributes button
        in the form view of the object. It opens a dinamically-built form view.

        :param ids: this is normally a singleton. If a longer list is passed,
                    we consider only the first item.

        """

        if context is None:
            context = {}

        model_data_pool = self.pool.get('ir.model.data')

        for lot in self.browse(cr, uid, ids, context=context):
            view_id = model_data_pool.get_object_reference(
                cr, uid,
                'production_lot_custom_attributes',
                'lot_attributes_form_view')[1]
            ctx = {
                'open_attributes': True,
                'attribute_group_ids': [
                    group.id for group in lot.attribute_group_ids
                ]
            }

            return {
                'name': 'Lot Attributes',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [view_id],
                'res_model': self._name,
                'context': ctx,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'res_id': lot.id,
            }

    def save_and_close_lot_attributes(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        def translate_view(source):
            """Return a translation of type view of source."""
            return translate(
                cr, None, 'view', context.get('lang'), source
            ) or source

        attr_pool = self.pool.get('attribute.attribute')
        result = super(stock_production_lot, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar=toolbar,
            submenu=submenu
        )
        if view_type == 'form' and context.get('attribute_group_ids'):
            eview = etree.fromstring(result['arch'])
            #hide button under the name
            button = eview.xpath("//button[@name='open_attributes']")
            if button:
                button = button[0]
                button.getparent().remove(button)
            attributes_notebook, toupdate_fields = (
                attr_pool._build_attributes_notebook(
                    cr, uid, context['attribute_group_ids'], context=context
                )
            )
            result['fields'].update(
                self.fields_get(cr, uid, toupdate_fields, context)
            )
            if context.get('open_attributes'):
                # i.e. the user pressed the open attributes button on the
                # form view. We put the attributes in a separate form view
                placeholder = eview.xpath(
                    "//separator[@string='attributes_placeholder']"
                )[0]
                placeholder.getparent().replace(
                    placeholder, attributes_notebook
                )
            elif context.get('open_lot_by_attribute_set'):
                # in this case, we know the attribute set beforehand, and we
                # add the attributes to the current view
                main_page = etree.Element(
                    'page', string=translate_view('Custom Attributes')
                )
                main_page.append(attributes_notebook)
                info_page = eview.xpath(
                    "//page[@string='%s']" % (translate_view('Stock Moves'),)
                )[0]
                info_page.addnext(main_page)
            result['arch'] = etree.tostring(eview, pretty_print=True)
        return result
