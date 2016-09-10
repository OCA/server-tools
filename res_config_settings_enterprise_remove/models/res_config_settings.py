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

        if page_name == 'account settings':
            doc = self._remove_enterprise_fields(
                i=1,
                doc=doc,
                custom_queries=[
                    "//div[@name='bank_statement_import_options'] \
                        /preceding-sibling::label[1]",
                    "//div[@name='bank_statement_import_options']",
                    "//div[div[field[@name='module_account_sepa']]] \
                        /preceding-sibling::label[1]",
                    "//div[div[field[@name='module_account_sepa']]]",
                ],
            )
        elif page_name == 'sale settings':
            doc = self._remove_enterprise_fields(
                i=2,
                doc=doc,
                custom_queries=[
                    "//field[@name='module_crm_voip']",
                ],
            )
        else:
            doc = self._remove_enterprise_fields(i=2, doc=doc)

        ret_val['arch'] = etree.tostring(doc)
        return ret_val

    @api.model
    def _remove_enterprise_fields(self, i, doc, i_end=0, custom_queries=None):

        if custom_queries:
            for query in custom_queries:
                items = doc.xpath(query)
                for item in items:
                    item.getparent().remove(item)

        while i >= i_end:
            items = doc.xpath(
                "//" +
                "div[" * i +
                "field[@widget='upgrade_boolean']" +
                "]" * i +
                "/preceding-sibling::label[1]"
            )
            items += doc.xpath(
                "//" +
                "div[" * i +
                "field[@widget='upgrade_boolean']" +
                "]" * i
            )
            for item in items:
                item.getparent().remove(item)
            i -= 1

        return doc
