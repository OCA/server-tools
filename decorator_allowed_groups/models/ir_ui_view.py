# Copyright (C) 2021-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.model
    def postprocess(self, model, node, view_id, in_tree_view, model_fields):
        if node.tag in ["a", "button"] and node.get("name", False):
            func = getattr(self.env[model], node.get("name"), False)
            if func:
                group_xml_ids = getattr(func, "_allowed_groups", False)
                if group_xml_ids:
                    node.set("groups", ",".join(group_xml_ids))
        return super().postprocess(
            model, node, view_id, in_tree_view, model_fields)
