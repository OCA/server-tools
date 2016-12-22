# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# DON'T IMPORT THIS MODULE IN INIT TO AVOID THE CREATION OF THE MODELS
# DEFINED FOR TESTS INTO YOUR ODOO INSTANCE

from odoo import fields, models


class SelectionGroupFullTestModel(models.Model):
    _name = 'selection.group.full.test.model'
    _rec_name = 'name'
    _abstract = True

    name = fields.Char(required=True)
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'),
                              ('closed', 'Closed')],
                             group_full=['in_progress'],
                             default='new')
