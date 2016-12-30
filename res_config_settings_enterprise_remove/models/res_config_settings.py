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

        page_name = ret_val['name']
        doc = etree.XML(ret_val['arch'])

        queries = []
        if page_name == 'account settings':
            queries += [
                "//div[field[@name='module_account_reports' and \
                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_reports_followup' and \
                    @widget='upgrade_boolean']]",
                "//div[field[@name='module_account_batch_deposit' and \
                    @widget='upgrade_boolean']]",
            ]

        queries += [
            "//div[div[field[@widget='upgrade_boolean']]] \
                /preceding-sibling::label[1]",
            "//div[div[field[@widget='upgrade_boolean']]]",
            "//div[field[@widget='upgrade_boolean']] \
                /preceding-sibling::label[1]",
            "//div[field[@widget='upgrade_boolean']]",
            "//field[@widget='upgrade_boolean']",
        ]

        for query in queries:
            for item in doc.xpath(query):
                item.getparent().remove(item)

        ret_val['arch'] = etree.tostring(doc)
        return ret_val
