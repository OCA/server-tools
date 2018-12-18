# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.depends('perm_read', 'perm_write', 'perm_create', 'perm_unlink')
    def compute_perm_int_vals(self):
        for res in self:
            res.update({'read_int': int(res.perm_read),
                        'write_int': int(res.perm_write),
                        'create_int': int(res.perm_create),
                        'unlink_int': int(res.perm_unlink),
                        })

    create_int = fields.Integer(compute=compute_perm_int_vals, store=True)
    write_int = fields.Integer(compute=compute_perm_int_vals, store=True)
    read_int = fields.Integer(compute=compute_perm_int_vals, store=True)
    unlink_int = fields.Integer(compute=compute_perm_int_vals, store=True)


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.depends('perm_read', 'perm_write', 'perm_create', 'perm_unlink')
    def compute_perm_int_vals(self):
        for res in self:
            res.update({'read_int': int(res.perm_read),
                        'write_int': int(res.perm_write),
                        'create_int': int(res.perm_create),
                        'unlink_int': int(res.perm_unlink),
                        })

    create_int = fields.Integer(compute=compute_perm_int_vals, store=True)
    write_int = fields.Integer(compute=compute_perm_int_vals, store=True)
    read_int = fields.Integer(compute=compute_perm_int_vals, store=True)
    unlink_int = fields.Integer(compute=compute_perm_int_vals, store=True)


class IrGroup(models.Model):
    _inherit = 'res.groups'

    all_rules_ids = fields.Many2many('ir.rule', 'rule_all_group_rel',
                                     'group_id', 'rule_id', string='Rules',
                                     domain=[('global', '=', False)])
    all_menus_ids = fields.Many2many('ir.ui.menu', 'ir_ui_all_menu_group_rel'
                                     'group_id', 'menu_id',
                                     string='Menus')
    all_views_ids = fields.Many2many('ir.ui.view', 'ir_ui_all_view_group_rel',
                                     'group_id', 'view_id', string='Views')
    all_access_ids = fields.Many2many('ir.model.access',
                                      'ir_ui_all_model_group_rel',
                                      'group_id', 'access_id', string='Access')

    @api.multi
    def button_compute_all_groups(self):
        for group in self:
            all_groups = group.trans_implied_ids
            # compute all menus
            all_menus = all_groups.mapped('menu_access')
            all_menus_ids = [(6, 0, all_menus.ids)]
            # compute all rules
            all_rules = all_groups.mapped('rule_groups')
            all_rules_ids = [(6, 0, all_rules.ids)]
            # compute all views
            all_views = all_groups.mapped('view_access')
            all_views_ids = [(6, 0, all_views.ids)]
            # compute all model access
            all_models = all_groups.mapped('model_access')
            all_access_ids = [(6, 0, all_models.ids)]

            group.write({'all_menus_ids': all_menus_ids,
                         'all_rules_ids': all_rules_ids,
                         'all_views_ids': all_views_ids,
                         'all_access_ids': all_access_ids,
                         })
