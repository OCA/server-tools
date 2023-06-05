# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ConditionalImage(models.Model):
    _name = "conditional.image"
    _description = "Conditional Image"
    _inherit = ["image.mixin"]

    name = fields.Char(required=True)
    model_name = fields.Char(required=True)
    selector = fields.Text(
        help="Python expression used as selector when multiple images are used"
        "for the same object. The variable `object` refers "
        "to the actual record on which the expression will be executed. "
        "An empty expression will always return `True`.",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        help="Company related check. If inherited object does not have a "
        "`company_id` field, it will be ignored. "
        "The check will first take the records with a company then, "
        "if no match is found, the ones without a company.",
    )
