# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TestOnchangeHelperCategory(models.Model):

    _name = "test_onchange_helper.category"
    _description = "Test Onchange Helper Category"

    name = fields.Char(required=True)
    parent = fields.Many2one(_name)
    root_categ = fields.Many2one(_name)
    display_name = fields.Char()
    computed_display_name = fields.Char(
        compute="_compute_computed_display_name"
    )

    @api.onchange("name", "parent")
    def _onchange_name_or_parent(self):
        if self.parent:
            self.display_name = self.parent.display_name + " / " + self.name
        else:
            self.display_name = self.name

    @api.onchange("parent")
    def _onchange_parent(self):
        current = self
        while current.parent:
            current = current.parent
        if current == self:
            self.root_categ = False
        else:
            self.root_categ = current

    @api.depends("name", "parent.display_name")
    def _compute_computed_display_name(self):
        for cat in self:
            if cat.parent:
                self.display_name = cat.parent.display_name + " / " + cat.name
            else:
                cat.display_name = cat.name
