# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from lxml import etree


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):

        ret_val = super(ResConfigSettings, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )

        page_name = ret_val['name']
        doc = etree.XML(ret_val['arch'])

        queries = []
        if page_name == 'account settings':
            queries += [
                "//div[field[@name='module_account_reports' and \
                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_deferred_revenue' and \
                                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_yodlee' and \
                                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_plaid' and \
                                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_bank_statement_import_qif' "
                "and @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_bank_statement_import_ofx' "
                "and @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_bank_statement_import_csv' "
                "and @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_sepa' and \
                                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_l10n_us_check_printing' and \
                                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_reports_followup' and \
                                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_batch_deposit' and "
                "@widget='upgrade_boolean']]",
            ]
        elif page_name == 'sale settings':
            queries += [
                "//div[field[@name='module_crm_voip' and "
                "@widget='upgrade_boolean']]/preceding-sibling::label[1]",
                "//div[field[@name='module_crm_voip' and "
                "@widget='upgrade_boolean']]",
                "//group[@name='config_sign']",
                "//div[field[@name='module_sale_contract' and "
                "@widget='upgrade_boolean']]/preceding-sibling::label[1]",
                "//div[field[@name='module_sale_contract' and "
                "@widget='upgrade_boolean']]",
            ]

        elif page_name == 'stock settings':
            queries += [
                "//group[@name='shipping']",
                "//group[5]",
                "//div[field[@name='module_stock_barcode' and "
                "@widget='upgrade_boolean']]",
            ]

        elif page_name == 'mrp settings':
            queries += [
                "//group[3]",
            ]

        for query in queries:
            for item in doc.xpath(query):
                item.getparent().remove(item)

        ret_val['arch'] = etree.tostring(doc)
        return ret_val
