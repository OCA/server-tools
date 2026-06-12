# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models


class ResPartnerBase(models.Model):
    _inherit = "res.partner"

    full_text = fields.Searchable(
        fields={
            "name": "A",
            "street": "B",
            "city": "C",
        },
    )


class ResPartner(models.Model):
    _inherit = "res.partner"

    full_text = fields.Searchable(
        fields_add={
            "email": "B",
            "street": "C",
            "commercial_company_name": "D",
        },
    )


class ResUsers(models.Model):
    _inherit = "res.users"

    full_text = fields.Searchable(
        fields={
            "partner_info": "A",
            "login": "B",
            "signature": "D",
        },
        dictionary="finnish",
        compute="_compute_full_text",
        store=True,
    )

    @api.depends(
        "login",
        "signature",
        "partner_id.name",
        "partner_id.city",
        "partner_id.street",
    )
    def _compute_full_text(self):
        for record in self:
            record.full_text = {
                "login": record.login,
                "signature": record.signature,
                "partner_info": " ".join(
                    [
                        info
                        for info in (
                            record.partner_id.name,
                            record.partner_id.city,
                            record.partner_id.street,
                        )
                        if info
                    ]
                ),
            }
