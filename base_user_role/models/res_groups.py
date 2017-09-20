# coding: utf-8
# Copyright 2014 ABF OSIELL <http://osiell.com>
# Copyright 2017 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from lxml import etree

from openerp import api, models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def update_user_groups_view(self):
        """ Make group selection and checkboxes appear readonly when there
        are roles on the user """
        res = super(ResGroups, self).update_user_groups_view()
        view = self.env.ref('base.user_groups_view')
        xml = etree.fromstring(view.arch.encode('utf-8'))
        for field in xml.findall('field'):
            field.attrib['attrs'] = (
                "{'readonly': [('role_line_ids', '!=', [])]}")
        xml_content = etree.tostring(
            xml, pretty_print=True, xml_declaration=True, encoding="utf-8")
        view.write({'arch': xml_content})
        return res
