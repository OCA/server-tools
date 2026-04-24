"""Classes and backend functionality for Audit module"""

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Inspector(models.Model):
    """Audit Inspector class and functionality."""

    _name = "audit.inspector"
    _description = "Audit Inspector"

    res_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Linked User",
        help="Odoo user for this inspector (dashboards and access control).",
        index=True,
        ondelete="set null",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=False,
        ondelete="cascade",
        string="Linked Partner",
    )
    name = fields.Char(
        string="Inspector Name", required=True, help="Name of the audit inspector"
    )
    snapshot_ids = fields.One2many(
        comodel_name="audit.snapshot", inverse_name="inspector_id", string="Snapshots"
    )
    team_ids = fields.Many2many(
        comodel_name="audit.team",
        string="Teams",
    )

    # Optional: make the email visible directly on Inspector,
    # but keep it *related* to the partner record
    inspector_email = fields.Char(
        related="partner_id.email", store=True, readonly=False
    )

    # 'Name' already exists on res.partner, but we still want
    # a full-name field, so we compute it from the partner value
    full_name = fields.Char(compute="_compute_full_name", store=True)
    forename = fields.Char()
    surname = fields.Char()
    active = fields.Boolean(default=True)

    @api.depends("partner_id", "partner_id.name", "name")
    def _split_name(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.name:
                parts = rec.partner_id.name.split(" ", 1)
                rec.forename = parts[0]
                rec.surname = parts[1] if len(parts) > 1 else ""

            elif rec.name:
                parts = rec.name.split(" ", 1)
                rec.forename = parts[0]
                rec.surname = parts[1] if len(parts) > 1 else ""

            else:
                rec.forename = ""
                rec.surname = ""

    @api.depends("partner_id", "partner_id.name", "forename", "surname")
    def _compute_full_name(self):
        """Optional helper if you still want a display name field."""

        for rec in self:
            if rec.partner_id and rec.partner_id.name:
                rec.full_name = rec.partner_id.name

            elif rec.forename or rec.surname:
                rec.full_name = f"{rec.forename or ''} {rec.surname or ''}".strip()

            else:
                rec.full_name = rec.name or "Unnamed Inspector"

    @api.model_create_multi
    def create(self, vals_list):
        """Ensure partner has required fields for delegation inheritance"""
        for vals in vals_list:
            # If no partner_id provided, we need to ensure the partner gets a name
            if not vals.get("partner_id"):
                # Build a name from available fields
                name_parts = []
                if vals.get("forename"):
                    name_parts.append(vals["forename"])
                if vals.get("surname"):
                    name_parts.append(vals["surname"])

                if name_parts:
                    # Use the constructed name
                    vals["name"] = " ".join(name_parts)
                elif vals.get("inspector_email"):
                    # Use email as fallback name
                    vals["name"] = vals["inspector_email"]
                elif not vals.get("name"):
                    # Last resort - use a generic name
                    vals["name"] = "Inspector"

        return super().create(vals_list)
