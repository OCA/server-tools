# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import groupby


class ConditionalImage(models.Model):
    _name = "conditional.image"
    _description = "Conditional Image"
    _inherit = ["image.mixin", "mail.thread"]
    _order = "sequence"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(required=True, default=100)
    default = fields.Boolean()
    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model", ondelete="cascade", required=True)
    model_name = fields.Char(string="Model Name", related="model_id.model")
    selector = fields.Text(
        help="Python expression used as selector when multiple images are used"
        "for the same object. The variable `object` refers "
        "to the actual record on which the expression will be executed. "
        "An empty expression will always return `True`.",
    )

    @api.constrains("default")
    def _check_default(self):
        defaults = self.search([("default", "=", True)])
        defaults_by_models = groupby(defaults, lambda i: i.model_name)

        # First we need to ensure there at least one default for this model
        if not defaults_by_models:
            missing_default_models = [self.model_name]
        else:
            missing_default_models = [
                model for model, images in defaults_by_models if not images
            ]
        if missing_default_models:
            raise ValidationError(
                _("You need at first a default for these models: ")
                + ", ".join(missing_default_models)
            )

        # Then we need to ensure there is only one default for this model
        multiple_defaults = any(
            [len(images) > 1 for model, images in defaults_by_models]
        )
        if multiple_defaults:
            raise ValidationError(_("You already have a default for this model!"))
