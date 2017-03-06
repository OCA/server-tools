# -*- coding: utf-8 -*-
# Copyright 2017 Specialty Medical Drugstore
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


_STATE = [
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'Pending'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
    ('exception', 'Exception')]


class BaseKanbanStage(models.Model):
    _inherit = 'base.kanban.stage'

    state = fields.Selection(_STATE, 'State')
