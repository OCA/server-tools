"""Classes and backend functionality for Audit module"""

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class DomainTargetRel(models.Model):
    """M2M link between audit domains and targets (one target per domain row)."""

    _name = "audit.domain_target_rel"
    _description = "Audit Domain Target Relation"
    _rec_name = "target_id"
    _order = "id asc"

    _unique_domain_target = models.Constraint(
        "unique(domain_id, target_id)",
        "This target is already linked to the domain.",
    )

    domain_id = fields.Many2one(
        comodel_name="audit.domain",
        string="Audit Domain",
        required=True,
        ondelete="cascade",
    )
    target_id = fields.Many2one(
        comodel_name="audit.target",
        string="Audit Target",
        required=True,
        ondelete="cascade",
    )


class Target(models.Model):
    """
    Target class, every Audit will have one or many targets linked to its Domain.
    A specific item within a domain that is being audited
    """

    _name = "audit.target"
    _description = "Audit Target"
    _order = "name asc"

    name = fields.Text()
    domain_id = fields.Many2one(
        comodel_name="audit.domain", string="Audit Domain", required=False
    )

    domain_rel_ids = fields.Many2many(
        comodel_name="audit.domain",
        relation="audit_domain_target_rel",
        column1="target_id",
        column2="domain_id",
        string="Linked Audit Domains",
    )

    snapshot_ids = fields.One2many(
        comodel_name="audit.snapshot",
        inverse_name="target_id",
        string="Audit Snapshots",
    )

    all_domain_rel_ids = fields.Many2many(
        comodel_name="audit.domain",
        compute="_compute_all_domain_ids",
        inverse="_inverse_all_domain_ids",
        string="All Domains",
        store=False,  # Do not store, computed dynamically
    )

    @api.depends("domain_id", "domain_rel_ids")
    def _compute_all_domain_ids(self):
        """Compute a Many2many field combining Main Domain and Related Domains"""
        for record in self:
            domain_records = record.domain_rel_ids
            if record.domain_id:
                domain_records |= record.domain_id  # Add the primary domain

            record.all_domain_rel_ids = domain_records  # Assign the merged domains

    def _inverse_all_domain_ids(self):
        """Ensure new domain added via UI are linked to Many2many (`domain_rel_ids`)"""
        for record in self:
            record.domain_rel_ids = record.all_domain_rel_ids

    @api.model
    def create(self, vals_list):
        """Set ``domain_id`` if missing; reject duplicate target names."""
        # Handle both single dict and list of dicts
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            # Set domain_id from all_domain_rel_ids if missing
            if not vals.get("domain_id") and vals.get("all_domain_rel_ids"):
                domain_rel_ids = (
                    vals["all_domain_rel_ids"][0][2]
                    if isinstance(vals["all_domain_rel_ids"], list)
                    else []
                )
                if domain_rel_ids:
                    vals["domain_id"] = domain_rel_ids[0]

            # Prevent duplicate targets with the same name in the same domain
            existing_target = self.env["audit.target"].search(
                [("name", "=", vals.get("name"))], limit=1
            )

            if existing_target:
                raise ValidationError(
                    self.env._(
                        "A target with the name '%(name)s' already exists !",
                        name=vals.get("name"),
                    )
                )

        # Call parent create method with the processed vals_list
        return super().create(vals_list)

    def link_to_domain(self, domain_id, target_id):
        """
        Check if link exists already, if not link it
        """
        domain_links = self.env["audit.domain_target_rel"].search(
            [("target_id", "=", target_id), ("domain_id", "=", domain_id)]
        )
        if bool(domain_links) is False:
            self.env["audit.domain_target_rel"].create(
                {
                    "domain_id": domain_id,
                    "target_id": target_id,
                }
            )

    def merge(self):
        """
        This will find matching targets then overwrite their IDs in the snapshot table
        """
        if self.domain_id:
            self.link_to_domain(self.domain_id.id, self.id)
        matching_targets = self.env["audit.target"].search([("name", "=", self.name)])
        for matching_target in matching_targets:
            if matching_target.id != self.id:
                # Move snapshots to original target
                for snapshot in self.env["audit.snapshot"].search(
                    [("target_id", "=", matching_target.id)]
                ):
                    snapshot.target_id = self.id
                # Check for domains that need to be merged as well
                if matching_target.domain_id:
                    self.link_to_domain(matching_target.domain_id.id, self.id)
                matching_target.unlink()
        self.domain_id = False

    def write(self, vals):
        """Update domain from related fields and block duplicate target names."""
        for record in self:
            new_name = vals.get("name", record.name)
            duplicate = self.env["audit.target"].search(
                [
                    ("name", "=", new_name),
                    ("id", "!=", record.id),  # Exclude current record to allow updates
                ],
                limit=1,
            )

            if duplicate:
                raise ValidationError(
                    self.env._(
                        "A target with the name '%(name)s' already exists !",
                        name=new_name,
                    )
                )

        # Ensure domain_id is assigned if missing
        res = super().write(vals)
        for record in self:
            if not record.domain_id and record.all_domain_rel_ids:
                record.domain_id = record.all_domain_rel_ids[0]

        return res
