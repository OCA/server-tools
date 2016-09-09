# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api
from lxml import etree
from openerp.addons.base.res.res_config import \
    res_config_settings


class ResConfigSettings(res_config_settings):

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):

        ret_val = super(ResConfigSettings, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            context=context,
            toolbar=toolbar,
            submenu=submenu,
        )

        doc = etree.XML(ret_val['arch'])

        # Remove Individual Elements
        xpath_specific_queries = [
            # Sale
            "//div[field[@name='module_sale_contract']] \
                /preceding-sibling::label[1]",
            # Inventory
            "//div[div[field[@name='module_delivery_dhl']]] \
                /preceding-sibling::label[1]",
            "//div[div[field[@name='module_stock_barcode']]] \
                /preceding-sibling::label[1]",
            # Invoicing
            "//a[@href='https://www.odoo.com/page/accounting-features']",
            "//div[@name='bank_statement_import_options'] \
                /preceding-sibling::label[1]",
            "//div[@name='bank_payments']/preceding-sibling::label[1]",
            # Project
            "//div[div[field[@name='module_project_forecast']]] \
                /preceding-sibling::label[1]",
            "//div[field[@name='module_project_timesheet_synchro']] \
                /preceding-sibling::label[1]",
            # WebsiteAdmin
            "//div[div[field[@name='module_website_form_editor']]] \
                /preceding-sibling::label[1]",
        ]

        for query in xpath_specific_queries:
            items = doc.xpath("%s" % query)
            for item in items:
                item.getparent().remove(item)

        # Bulk Remove Fields and Labels
        upgrade_fields = doc.xpath("//field[@widget='upgrade_boolean']")
        for field in upgrade_fields:
            for label in doc.xpath("//label[@for='%s']" % field.get('name')):
                label.getparent().remove(label)
            field.getparent().remove(field)

        # Clean Up Empty Divs
        complete = False
        while not complete:
            divs = doc.xpath("//div[not(*)]")
            if not divs:
                complete = True
            else:
                for div in divs:
                    div.getparent().remove(div)

        ret_val['arch'] = etree.tostring(doc)
        return ret_val
