# -*- coding: utf-8 -*-
"""Classes and backend functionality for Audit module"""

import logging
import random

from odoo import Command, api, fields, models

_logger = logging.getLogger(__name__)


# We can add things that can be audited here
class Domain(models.Model):
    """
    Domain class, every Audit must have a unique Domain.
    This represents a class of things that can be audited.  Such as
    retail stores, or software security.  Within a domain we can audit individual items.
    """

    _name = "audit.domain"
    _description = "Audit Domain"

    # We should not let duplicate domains to be created
    _name_uniq = models.Constraint(
        "unique (name)",
        "'Domain Name' must be unique, this domain name already exists.",
    )

    name = fields.Text()

    target_ids = fields.One2many(
        comodel_name="audit.target", inverse_name="domain_id", string="Audit Targets"
    )

    target_rel_ids = fields.Many2many(
        comodel_name="audit.target",
        relation="audit_domain_target_rel",
        column1="domain_id",
        column2="target_id",
        string="Audit Targets (Many2many)",
    )

    section_ids = fields.One2many(
        comodel_name="audit.section", inverse_name="domain_id", string="Audit Sections"
    )

    all_target_rel_ids = fields.Many2many(
        comodel_name="audit.target",
        compute="_compute_all_target_ids",
        inverse="_inverse_all_target_ids",
        string="All Targets",
        store=False,  # Do not store since it's computed dynamically
    )

    @api.depends("target_ids", "target_rel_ids")
    def _compute_all_target_ids(self):
        """Compute a combined Many2many field of all targets (One2many + Many2many)"""
        for record in self:
            target_records = record.target_ids | record.target_rel_ids
            record.all_target_rel_ids = target_records  # Assign merged targets

    def _inverse_all_target_ids(self):
        """Ensure new targets added via UI are linked to Many2many (`target_rel_ids`)"""
        for record in self:
            record.target_rel_ids = record.all_target_rel_ids

    # Duplicate Audit Design all related section with questions
    def action_duplicate_domain(self):
        """Duplicate the audit domain and update Many2many relationships correctly."""
        for record in self:
            unique_key = random.randint(1, 100000)
            # Temporary name until the user renames; domain names are unique.
            new_domain = record.copy(
                {"name": f"{record.name} - Duplicate_{unique_key}"}
            )

            # Duplicate Sections & Questions
            section_mapping = {}
            for section in record.section_ids:
                new_section = section.copy({"domain_id": new_domain.id})
                section_mapping[section.id] = new_section.id

                for question in section.question_ids:
                    question.copy({"section_id": new_section.id})

            # Add targets to relationship table doesn't need to duplicate it
            for target in record.target_ids:
                new_domain.write({"target_rel_ids": [Command.link(target.id)]})

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Success",
                    "message": f"Domain '{new_domain.name}' duplicated successfully!",
                    "sticky": False,
                    "type": "success",
                },
            }
