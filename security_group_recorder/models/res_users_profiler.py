# Copyright 2023 ForgeFlow S.L. (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import api, fields, models


class UserProfilerSessions(models.Model):
    _name = "res.users.profiler.sessions"
    _description = "User Profiler Sessions"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
    )
    active = fields.Boolean(
        default=False,
        string="Log",
    )
    profiled_accesses_ids = fields.One2many(
        comodel_name="res.users.profiler.accesses",
        inverse_name="session_id",
        string="Profiled Accesses",
    )
    profiled_actions_ids = fields.One2many(
        comodel_name="res.users.profiler.actions",
        inverse_name="session_id",
        string="Profiled Actions",
        readonly=True,
    )
    profiled_menus_ids = fields.One2many(
        comodel_name="ir.ui.menu",
        string="Profiled Menus",
        compute="_compute_menus",
    )
    implied_groups = fields.Many2many(
        comodel_name="res.groups",
        relation="res_users_profiler_sessions_groups_rel",
        column1="sid",
        column2="gid",
        string="Implied Groups",
        help="Choose which groups the user role will have.",
    )
    implied_menus = fields.One2many(
        comodel_name="ir.ui.menu",
        string="Implied Menus",
        compute="_compute_implied_menus",
        readonly=True,
    )

    @api.model
    def create(self, values):
        active_user_session = self.env["res.users.profiler.sessions"].search(
            [("active", "=", True), ("user_id", "=", self.env.user.id)]
        )
        if active_user_session:
            active_user_session.active = False

        return super().create(values)

    def _get_group_basic_menus(self, basic_menus, implied_group, groups_checked):
        for menu_access in implied_group.menu_access:
            if menu_access.id not in basic_menus:
                basic_menus.append(menu_access.id)

        if implied_group.implied_ids:
            for implied_group in implied_group.implied_ids:
                if implied_group not in groups_checked:
                    groups_checked.append(implied_group)
                    aux_basic_menus = self._get_group_basic_menus(
                        basic_menus, implied_group, groups_checked
                    )
                    basic_menus = list(set(basic_menus + aux_basic_menus))

        return basic_menus

    def _is_basic_menu(self, menu_id):
        basic_menus = []
        basic_security_group = (
            self.env["res.groups"].sudo().search([("name", "=", "Internal User")])
        )
        groups_checked = []
        groups_checked.append(basic_security_group)
        basic_menus = self._get_group_basic_menus(
            basic_menus, basic_security_group, groups_checked
        )
        if menu_id not in basic_menus:
            return False
        else:
            return True

    def _update_menus(self, all_menus):
        real_menus = []
        for menu in all_menus:
            if not self._is_basic_menu(menu.id):
                real_menus.append(menu.id)

        if not real_menus:
            real_menus = self.env["ir.ui.menu"]

        return real_menus

    @api.depends("profiled_actions_ids.action_id", "profiled_actions_ids.action_type")
    def _compute_menus(self):
        for rec in self:
            all_menus = self.env["ir.ui.menu"]
            for profiled_actions in rec.profiled_actions_ids:
                all_menus |= profiled_actions.menu_ids
            not_basic_menus = self._update_menus(all_menus)
            rec.profiled_menus_ids = not_basic_menus

    @api.depends("implied_groups", "profiled_menus_ids")
    def _compute_implied_menus(self):
        for rec in self:
            implied_groups = rec.implied_groups | rec.implied_groups.mapped(
                "implied_ids"
            )
            menus = implied_groups.mapped("menu_access")
            rec.implied_menus = rec.profiled_menus_ids.filtered(lambda m: m in menus)


class UserProfilerAccesses(models.Model):
    _name = "res.users.profiler.accesses"
    _description = "User Profiler Accesses"

    name = fields.Char(index=True)

    session_id = fields.Many2one(
        comodel_name="res.users.profiler.sessions",
        string="Profiler Session",
        required=True,
        ondelete="cascade",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        related="session_id.user_id",
        readonly=True,
        store=True,
    )
    res_model = fields.Char(
        string="Model Name",
        required=True,
    )

    perm_read = fields.Boolean(
        string="Read",
    )
    perm_write = fields.Boolean(
        string="Write",
    )
    perm_create = fields.Boolean(
        string="Create",
    )
    perm_unlink = fields.Boolean(
        string="Delete",
    )


class UserProfilerActions(models.Model):
    _name = "res.users.profiler.actions"
    _description = "User Profiler Actions"

    session_id = fields.Many2one(
        comodel_name="res.users.profiler.sessions",
        string="Profiler Session",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        related="session_id.user_id",
        readonly=True,
        store=True,
    )
    action_id = fields.Integer(
        string="Action Id",
        readonly=True,
    )
    action_type = fields.Char(
        string="Action Type",
        readonly=True,
        help="The type of the Action.",
    )
    action = fields.Reference(
        selection=[
            ("ir.actions.report", "ir.actions.report"),
            ("ir.actions.act_window", "ir.actions.act_window"),
            ("ir.actions.act_url", "ir.actions.act_url"),
            ("ir.actions.server", "ir.actions.server"),
            ("ir.actions.client", "ir.actions.client"),
            ("ir.actions.actions", "ir.actions.actions"),
        ],
        compute="_compute_action",
        readonly=True,
        store=False,
    )
    action_name = fields.Char(
        string="Action Name",
        readonly=True,
    )
    res_model = fields.Char(
        string="Model Name",
        required=True,
        readonly=True,
    )
    menu_ids = fields.One2many(
        comodel_name="ir.ui.menu",
        string="Menus",
        compute="_compute_menus",
        readonly=True,
    )

    @api.depends("action_id", "action_type")
    def _compute_action(self):
        for rec in self:
            if rec.action_id and rec.action_type:
                rec.action = self.env[rec.action_type].browse(rec.action_id)

    @api.depends("action_id", "action_type")
    def _compute_menus(self):
        def _get_menu_parents(env, _menu):
            parents = env["ir.ui.menu"]
            if _menu.parent_id:
                parents |= _get_menu_parents(env, _menu.parent_id)
            return parents | _menu

        all_menus = self.env["ir.ui.menu"].search([])
        for rec in self:
            if rec.action_id and rec.action_type:
                menu_ids = all_menus.filtered(
                    lambda m: m.action
                    and m.action.id == rec.action_id
                    and m.action.type == rec.action_type
                )
                menu_parent_ids = self.env["ir.ui.menu"]
                for menu in menu_ids:
                    menu_parent_ids |= _get_menu_parents(self.env, menu).filtered(
                        lambda m: m.groups_id
                    )
                rec.menu_ids = menu_ids | menu_parent_ids
            else:
                rec.menu_ids = self.env["ir.ui.menu"]
