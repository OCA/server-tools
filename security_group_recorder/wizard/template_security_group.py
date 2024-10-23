from odoo import api, fields, models

from ..models.ir_model import _postprocess_check_access_rights


class TemplateSecurityGroup(models.TransientModel):
    _name = "template.security.group"
    _description = "Create Security Group From Template"

    category_id = fields.Many2one(
        "ir.module.category", string="Application", index=True
    )
    name = fields.Char(required=True, translate=True, default="Your Group Name")
    share = fields.Boolean(
        string="Share Group",
        help="Group created to set access rights for sharing data with some users.",
    )
    users = fields.Many2many("res.users")
    implied_ids = fields.Many2many(
        "res.groups",
        string="Inherits",
        help="Users of this group automatically inherit those groups",
    )
    menu_access = fields.Many2many("ir.ui.menu", string="Access Menu")
    view_access = fields.Many2many("ir.ui.view", string="Views")
    model_access = fields.Many2many(
        "res.users.profiler.accesses", string="Access Controls", copy=True
    )
    rule_groups = fields.Many2many(
        "ir.rule", string="Rules", domain=[("global", "=", False)]
    )
    comment = fields.Text(translate=True)

    def category_id_prepare_value(self, active_user_session):
        parent_found = False
        if active_user_session.profiled_menus_ids:
            actual_menu = active_user_session.profiled_menus_ids[0]
            while not parent_found:
                parent = actual_menu.parent_id
                if not parent:
                    parent_found = True
                else:
                    actual_menu = parent
            return actual_menu
        else:
            return False

    @api.onchange("name")
    def model_access_compute_names(self):
        active_user_session = self.env["res.users.profiler.sessions"].search(
            [("active", "=", True), ("user_id", "=", self.env.user.id)]
        )
        for pa in active_user_session.profiled_accesses_ids:
            pa.name = pa.res_model + " " + self.name

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_user_session = self.env["res.users.profiler.sessions"].search(
            [("active", "=", True), ("user_id", "=", self.env.user.id)]
        )
        basic_group = self.env["res.groups"].search([("name", "=", "Internal User")])
        res["implied_ids"] = basic_group.ids
        res["users"] = self.env.user.ids
        res["menu_access"] = active_user_session.profiled_menus_ids.ids
        actual_menu = self.category_id_prepare_value(active_user_session)
        if actual_menu:
            category_id = (
                self.env["ir.module.category"]
                .search([("name", "=", actual_menu.name)], limit=1)
                .id
            )
            res["category_id"] = category_id
        model_access_ids = _postprocess_check_access_rights(
            self.env, active_user_session
        )
        res["model_access"] = model_access_ids

        return res

    def create_group(self):
        group_object = self.env["res.groups"]
        model_access_object = self.env["ir.model.access"]
        ir_model_object = self.env["ir.model"]
        real_model_access = []
        values = {}
        for ma in self.model_access:
            model_id = ir_model_object.search([("model", "=", ma.res_model)])
            values["name"] = ma.name
            values["model_id"] = model_id.id
            values["perm_create"] = ma.perm_create
            values["perm_write"] = ma.perm_write
            values["perm_read"] = ma.perm_read
            values["perm_unlink"] = ma.perm_unlink

            record = model_access_object.create(values)
            real_model_access.append(record.id)
        # hem de processar el model access
        vals = {
            "name": self.name,
            "implied_ids": self.implied_ids,
            "menu_access": self.menu_access,
            "users": self.users,
            "category_id": self.category_id.id,
            "share": self.share,
            "view_access": self.view_access,
            "rule_groups": self.rule_groups,
            "comment": self.comment,
            "model_access": real_model_access,
        }
        group_object.create(vals)

        active_user_session = self.env["res.users.profiler.sessions"].search(
            [("active", "=", True), ("user_id", "=", self.env.user.id)]
        )

        if active_user_session:
            active_user_session.active = False
        return True
