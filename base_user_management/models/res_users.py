from lxml import etree

from odoo import _, api, models
from odoo.exceptions import AccessError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_disallowed_groups(self):
        return ["base.group_erp_manager"]

    def _check_has_access_to_apply_groups(self):
        if self.user_has_groups(
            "base_user_management.group_access_right_security_manage_users"
        ):
            disallowed_groups = self._get_disallowed_groups()
            for user in self:
                for group in disallowed_groups:
                    not_statement = "!" in group
                    group = group.replace("!", "")
                    if (
                        not not_statement
                        and user.has_group(group)
                        or not_statement
                        and not user.has_group(group)
                    ):
                        raise AccessError(
                            _(
                                "You are not allowed to add / remove this group to users."
                            )
                        )

    def write(self, vals):
        res = super().write(vals)
        self._check_has_access_to_apply_groups()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._check_has_access_to_apply_groups()
        return res

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        """Remove the Administration / Settings option from the view"""
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        is_erp_manager = self.user_has_groups("base.group_erp_manager")
        if view_type == "form" and not is_erp_manager:
            disallowed_groups = self._get_disallowed_groups()
            for group in disallowed_groups:
                group = group.replace("!", "")
                erp_group_id = self.env.ref(group).id
                sel_xpath = (
                    "//field[contains(@name, 'sel_groups_%s_')]/.." % erp_group_id
                )
                in_xpath = "//field[@name='in_group_%s']" % erp_group_id
                xml = etree.XML(res["arch"])
                xml_groups = xml.xpath(sel_xpath) + xml.xpath(in_xpath)
                for xml_group in xml_groups:
                    xml_group.getparent().remove(xml_group)
                res["arch"] = etree.tostring(xml, encoding="unicode")
        return res
