# -*- coding: utf-8 -*-
"""Classes and backend functionality for Audit module"""

import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)


class Section(models.Model):
    """Section class, every Audit can have many sections."""

    _name = "audit.section"
    _description = "To group questions"

    name = fields.Text()
    question_ids = fields.One2many(
        comodel_name="audit.question", inverse_name="section_id", string="Questions"
    )
    domain_id = fields.Many2one(
        comodel_name="audit.domain", string="Domain Name", required=True
    )
