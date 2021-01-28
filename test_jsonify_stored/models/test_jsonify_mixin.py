# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TestJsonifyStored(models.Model):
    """Reference Implementation of the mixin.
    """

    _name = "test.jsonify.stored"
    _inherit = "jsonify.stored.mixin"

    _export_xmlid = "test_jsonify_stored.model_export"  # created in pre_init hook

    boolean = fields.Boolean()
    char = fields.Char()
    float = fields.Float()
    user_id = fields.Many2one("res.users")
