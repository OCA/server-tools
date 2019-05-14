# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class UserProfilerSessions(models.Model):
    _name = 'res.users.profiler.sessions'
    _description = "User Profiler Sessions"
    _order = "create_date,user_id,user_role_name,id"

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        required=True,
    )
    active = fields.Boolean(
        default=False,
        string='Log',
    )
    user_role_name = fields.Char(
        string='User Role Name',
        required=True,
    )
    profiled_accesses_ids = fields.One2many(
        comodel_name='res.users.profiler.accesses',
        inverse_name='session_id',
        string="Profiled Accesses",
        readonly=True,
    )
    profiled_actions_ids = fields.One2many(
        comodel_name='res.users.profiler.actions',
        inverse_name='session_id',
        string="Profiled Actions",
        readonly=True,
    )
    profiled_menus_ids = fields.One2many(
        comodel_name='ir.ui.menu',
        string="Profiled Menus",
        compute='_compute_menus',
        readonly=True,
    )
    implied_groups = fields.Many2many(
        comodel_name='res.groups',
        relation='res_users_profiler_sessions_groups_rel',
        column1='sid',
        column2='gid',
        string="Implied Groups",
        help="Choose which groups the user role will have.",
    )
    implied_menus = fields.One2many(
        comodel_name='ir.ui.menu',
        string="Implied Menus",
        compute='_compute_implied_menus',
        readonly=True,
    )

    @api.depends('profiled_actions_ids.action_id',
                 'profiled_actions_ids.action_type')
    def _compute_menus(self):
        for rec in self:
            all_menus = self.env['ir.ui.menu']
            for profiled_actions in rec.profiled_actions_ids:
                all_menus |= profiled_actions.menu_ids
            rec.profiled_menus_ids = all_menus

    @api.depends('implied_groups', 'profiled_menus_ids')
    def _compute_implied_menus(self):
        for rec in self:
            implied_groups = rec.implied_groups | rec.implied_groups.mapped(
                'implied_ids')
            menus = implied_groups.mapped('menu_access')
            rec.implied_menus = rec.profiled_menus_ids.filtered(
                lambda m: m in menus)

    @api.constrains('active')
    def _check_session_active_unique(self):
        """An user can have two active sessions at the same time."""
        for session in self:
            if session.active and len(
                    session.user_id.profiled_sessions_ids.filtered(
                        lambda s: s.active and s != session)) > 0:
                raise ValidationError(
                    _('The user %s already has a session active.') % (
                        session.user_id.display_name))


class UserProfilerAccesses(models.Model):
    _name = 'res.users.profiler.accesses'
    _description = "User Profiler Accesses"

    session_id = fields.Many2one(
        comodel_name='res.users.profiler.sessions',
        string='Profiler Session',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        related='session_id.user_id',
        readonly=True,
        store=True,
    )
    model_access_id = fields.Many2one(
        comodel_name='ir.model.access',
        string='Model Access',
        readonly=True,
    )
    res_model = fields.Char(
        string='Model Name',
        required=True,
        readonly=True,
    )
    count_read = fields.Integer(
        string='Reads',
        readonly=True,
    )
    count_write = fields.Integer(
        string='Writes',
        readonly=True,
    )
    count_create = fields.Integer(
        string='Creates',
        readonly=True,
    )
    count_unlink = fields.Integer(
        string='Deletes',
        readonly=True,
    )
    new_access = fields.Boolean(
        readonly=True,
        compute='_compute_is_new_access',
    )

    @api.depends('session_id.implied_groups')
    def _compute_is_new_access(self):
        for rec in self.sudo():
            implied_groups = rec.session_id.implied_groups | rec.session_id.\
                implied_groups.mapped('implied_ids')
            implied_accesses = implied_groups.mapped(
                'model_access').filtered(
                lambda a: a.model_id.model == rec.res_model and a in
                rec.session_id.profiled_accesses_ids.mapped('model_access_id'))
            if not implied_accesses:
                implied_accesses = self.env['ir.model.access'].search(
                    [('group_id', '=', False)]).filtered(
                    lambda a: a.model_id.model == rec.res_model and a in
                    rec.session_id.profiled_accesses_ids.mapped(
                        'model_access_id'))
            if not implied_accesses:
                rec.new_access = True
                continue
            if any([
                (rec.count_read and not ia.perm_read) or
                (rec.count_write and not ia.perm_write) or
                (rec.count_create and not ia.perm_create) or
                (rec.count_unlink and not ia.perm_unlink)
                for ia in implied_accesses
            ]):
                rec.new_access = True
                continue
            rec.new_access = False


class UserProfilerActions(models.Model):
    _name = 'res.users.profiler.actions'
    _description = "User Profiler Actions"

    session_id = fields.Many2one(
        comodel_name='res.users.profiler.sessions',
        string='Profiler Session',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User',
        related='session_id.user_id',
        readonly=True,
        store=True,
    )
    view_id = fields.Many2one(
        comodel_name='ir.ui.view',
        string='View',
        readonly=True,
    )
    action_id = fields.Integer(
        string='Action Id',
        readonly=True,
    )
    action_type = fields.Char(
        string='Action Type',
        readonly=True,
        help='The type of the Action.',
    )
    action = fields.Reference(
        selection=[
            ('ir.actions.report', 'ir.actions.report'),
            ('ir.actions.act_window', 'ir.actions.act_window'),
            ('ir.actions.act_url', 'ir.actions.act_url'),
            ('ir.actions.server', 'ir.actions.server'),
            ('ir.actions.client', 'ir.actions.client'),
            ('ir.actions.actions', 'ir.actions.actions'),
        ],
        compute='_compute_action',
        readonly=True,
        store=False,
    )
    action_name = fields.Char(
        string='Action Name',
        readonly=True,
    )
    method_name = fields.Char(
        string='Method Name',
        readonly=True,
        help='Python method that comes from clicked buttons or similar.',
    )
    res_model = fields.Char(
        string='Model Name',
        required=True,
        readonly=True,
    )
    count_action = fields.Integer(
        string='Clicks',
        readonly=True,
    )
    menu_ids = fields.One2many(
        comodel_name='ir.ui.menu',
        string='Menus',
        compute='_compute_menus',
        readonly=True,
    )
    new_action = fields.Boolean(
        readonly=True,
        compute='_compute_is_new_action',
    )

    @api.depends('action_id', 'action_type')
    def _compute_action(self):
        for rec in self:
            if rec.action_id and rec.action_type:
                rec.action = self.env[rec.action_type].browse(rec.action_id)

    @api.depends('action_id', 'action_type')
    def _compute_menus(self):

        def _get_menu_parents(env, _menu):
            parents = env['ir.ui.menu']
            if _menu.parent_id:
                parents |= _get_menu_parents(env, _menu.parent_id)
            return parents | _menu

        all_menus = self.env['ir.ui.menu'].search([])
        for rec in self:
            if rec.action_id and rec.action_type:
                menu_ids = all_menus.filtered(
                    lambda m: m.action and m.action.id == rec.action_id and
                    m.action.type == rec.action_type)
                menu_parent_ids = self.env['ir.ui.menu']
                for menu in menu_ids:
                    menu_parent_ids |= _get_menu_parents(self.env, menu).\
                        filtered(lambda m: m.groups_id)
                rec.menu_ids = menu_ids | menu_parent_ids
            else:
                rec.menu_ids = self.env['ir.ui.menu']

    @api.depends('session_id.implied_groups')
    def _compute_is_new_action(self):
        for rec in self.sudo():
            if rec.action_id and hasattr(rec.action, 'groups_id'):
                action_groups = rec.action.groups_id
                implied_groups = rec.session_id.implied_groups | rec.\
                    session_id.implied_groups.mapped('implied_ids')
                if any([g not in implied_groups for g in action_groups]):
                    rec.new_access = True
                    continue
            rec.new_access = False
