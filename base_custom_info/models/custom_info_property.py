# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class CustomInfoProperty(models.Model):
    """Name of the custom information property."""
    _description = "Custom information property"
    _name = "custom.info.property"
    _order = "template_id, category_sequence, category_id, sequence, id"
    _sql_constraints = [
        ("name_template",
         "UNIQUE (name, template_id)",
         "Another property with that name exists for that template."),
    ]

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(index=True)
    category_id = fields.Many2one(
        comodel_name="custom.info.category",
        string="Category",
    )
    category_sequence = fields.Integer(
        string="Category Sequence",
        related="category_id.sequence",
        store=True,
        readonly=True,
    )
    template_id = fields.Many2one(
        comodel_name='custom.info.template', string='Template',
        required=True, ondelete="cascade",
    )
    model = fields.Char(
        related="template_id.model", readonly=True, auto_join=True,
    )
    info_value_ids = fields.One2many(
        comodel_name="custom.info.value",
        inverse_name="property_id",
        string="Property Values")
    default_value = fields.Char(
        translate=True,
        help="Will be applied by default to all custom values of this "
             "property. This is a char field, so you have to enter some value "
             "that can be converted to the field type you choose.",
    )
    required = fields.Boolean()
    minimum = fields.Float(
        help="For numeric fields, it means the minimum possible value; "
             "for text fields, it means the minimum possible length. "
             "If it is bigger than the maximum, then this check is skipped",
    )
    maximum = fields.Float(
        default=-1,
        help="For numeric fields, it means the maximum possible value; "
             "for text fields, it means the maximum possible length. "
             "If it is smaller than the minimum, then this check is skipped",
    )
    field_type = fields.Selection(
        selection=[
            ("str", "Text"),
            ("int", "Whole number"),
            ("float", "Decimal number"),
            ("bool", "Yes/No"),
            ("id", "Selection"),
        ],
        default="str",
        required=True,
        help="Type of information that can be stored in the property.",
    )
    option_ids = fields.Many2many(
        comodel_name="custom.info.option",
        string="Options",
        help="When the field type is 'selection', choose the available "
             "options here.",
    )

    @api.multi
    def check_access_rule(self, operation):
        """You access a property if you access its template."""
        self.mapped("template_id").check_access_rule(operation)
        return super().check_access_rule(operation)

    def _check_default_value_one(self):
        if self.default_value:
            try:
                self.env["custom.info.value"]._transform_value(
                    self.default_value, self.field_type, self)
            except ValueError:
                selection = dict(
                    self._fields["field_type"].get_description(self.env)
                    ["selection"])
                raise ValidationError(
                    _("Default value %s cannot be converted to type %s.") %
                    (self.default_value, selection[self.field_type]))

    @api.constrains("default_value", "field_type")
    def _check_default_value(self):
        """Ensure the default value is valid."""
        for rec in self:
            rec._check_default_value_one()

    @api.multi
    @api.onchange("required", "field_type")
    def _onchange_required_warn(self):
        """Warn if the required flag implies a possible weird behavior."""
        if self.required:
            if self.field_type == "bool":
                raise UserError(
                    _("If you require a Yes/No field, you can only set Yes."))
            if self.field_type in {"int", "float"}:
                raise UserError(
                    _("If you require a numeric field, you cannot set it to "
                      "zero."))
