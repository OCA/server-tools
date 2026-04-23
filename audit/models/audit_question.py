# -*- coding: utf-8 -*-
"""Classes and backend functionality for Audit module"""

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Question(models.Model):
    """
    Question: each section has one or more questions; each domain has sections.
    """

    _name = "audit.question"
    _description = "Questions for the form"

    BOOLEAN = "boolean"
    INTEGER = "integer"
    FLOAT = "float"

    QUESTION_OPTIONS = [
        (BOOLEAN, "True / False"),
        (INTEGER, "Star Rating"),
        (FLOAT, "Percentage"),
    ]

    prompt = fields.Text()
    answer_type = fields.Selection(selection=QUESTION_OPTIONS, required=True)
    name = fields.Char(compute="_compute_name", store=True)
    section_id = fields.Many2one(comodel_name="audit.section", required=True)

    @api.depends("prompt")
    def _compute_name(self):
        for record in self:
            record.name = record.prompt
