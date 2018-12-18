# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    all_rules_ids = fields.Many2many('ir.rule', 'rule_all_user_rel',
                                     'user_id', 'rule_id', string='Rules',
                                     domain=[('global', '=', False)],
                                     readonly=True)
    all_menus_ids = fields.Many2many('ir.ui.menu', 'ir_ui_all_menu_user_rel'
                                     'user_id', 'menu_id',
                                     string='Menus', readonly=True)
    all_views_ids = fields.Many2many('ir.ui.view', 'ir_ui_all_view_user_rel',
                                     'user_id', 'view_id', string='Views',
                                     readonly=True)
    all_access_ids = fields.Many2many('ir.model.access',
                                      'ir_ui_all_model_user_rel',
                                      'user_id', 'access_id', string='Access',
                                      readonly=True)
    trans_group_implied_ids = fields.Many2many('res.groups',
                                               'res_groups_all_user_rel',
                                               'user_id', 'group_id',
                                               string="Groups")

    @api.multi
    def button_compute_all_groups(self):
        for user in self:
            all_groups = user.groups_id
            all_groups.button_compute_all_groups()
            # compute all menus
            all_menus_ids = [(6, 0, all_groups.mapped('all_menus_ids').ids)]
            # compute all rules
            all_rules_ids = [(6, 0, all_groups.mapped('all_rules_ids').ids)]
            # compute all views
            all_views_ids = [(6, 0, all_groups.mapped('all_views_ids').ids)]
            # compute all model access
            all_access_ids = [(6, 0, all_groups.mapped('all_access_ids').ids)]
            # compute all model access
            trans_group_implied_ids = (
                [(6, 0, all_groups.mapped('trans_implied_ids').ids)]
            )
            user.write({'all_menus_ids': all_menus_ids,
                        'all_rules_ids': all_rules_ids,
                        'all_views_ids': all_views_ids,
                        'all_access_ids': all_access_ids,
                        'trans_group_implied_ids': trans_group_implied_ids,
                        })

    @api.model
    def cron_compute_all_groups(self):
        self.search([]).button_compute_all_groups()
