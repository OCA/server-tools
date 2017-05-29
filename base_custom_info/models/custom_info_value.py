# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class CustomInfoValue(models.Model):
    _description = "Custom information value"
    _name = "custom.info.value"
    _rec_name = 'value'
    _order = ("model, res_id, category_sequence, category_id, "
              "property_sequence, property_id")
    _sql_constraints = [
        ("property_owner",
         "UNIQUE (property_id, model, res_id)",
         "Another property with that name exists for that resource."),
    ]

    model = fields.Char(
        related="property_id.model", index=True, readonly=True,
        auto_join=True, store=True,
    )
    owner_id = fields.Reference(
        selection="_selection_owner_id", string="Owner",
        compute="_compute_owner_id", inverse="_inverse_owner_id",
        help="Record that owns this custom value.",
    )
    res_id = fields.Integer(
        string="Resource ID", required=True, index=True, store=True,
        ondelete="cascade",
    )
    property_id = fields.Many2one(
        comodel_name='custom.info.property', required=True, string='Property',
        readonly=True,
    )
    property_sequence = fields.Integer(
        related="property_id.sequence", store=True, index=True, readonly=True,
    )
    category_sequence = fields.Integer(
        related="property_id.category_id.sequence", store=True, readonly=True,
    )
    category_id = fields.Many2one(
        related="property_id.category_id", store=True, readonly=True,
    )
    name = fields.Char(related='property_id.name', readonly=True)
    field_type = fields.Selection(
        related="property_id.field_type", readonly=True,
    )
    field_name = fields.Char(
        compute="_compute_field_name",
        help="Technical name of the field where the value is stored.",
    )
    required = fields.Boolean(related="property_id.required", readonly=True)
    value = fields.Char(
        compute="_compute_value", inverse="_inverse_value",
        search="_search_value",
        help="Value, always converted to/from the typed field.",
    )
    value_str = fields.Char(string="Text value", translate=True, index=True)
    value_int = fields.Integer(string="Whole number value", index=True)
    value_float = fields.Float(string="Decimal number value", index=True)
    value_bool = fields.Boolean(string="Yes/No value", index=True)
    value_id = fields.Many2one(
        comodel_name="custom.info.option", string="Selection value",
        ondelete="cascade", domain="[('property_ids', 'in', [property_id])]",
    )

    @api.multi
    def check_access_rule(self, operation):
        """You access a value if you access its owner record."""
        if self.env.uid != SUPERUSER_ID:
            for record in self.filtered('owner_id'):
                record.owner_id.check_access_rights(operation)
                record.owner_id.check_access_rule(operation)
        return super(CustomInfoValue, self).check_access_rule(operation)

    @api.model
    def _selection_owner_id(self):
        """You can choose among models linked to a template."""
        models = self.env["ir.model.fields"].search([
            ("ttype", "=", "many2one"),
            ("relation", "=", "custom.info.template"),
            ("model_id.transient", "=", False),
            "!", ("model", "=like", "custom.info.%"),
        ]).mapped("model_id")
        models = models.search([("id", "in", models.ids)], order="name")
        return [(m.model, m.name) for m in models
                if m.model in self.env and self.env[m.model]._auto]

    @api.multi
    @api.depends("property_id.field_type")
    def _compute_field_name(self):
        """Get the technical name where the real typed value is stored."""
        for s in self:
            s.field_name = "value_{!s}".format(s.property_id.field_type)

    @api.multi
    @api.depends("res_id", "model")
    def _compute_owner_id(self):
        """Get the id from the linked record."""
        for record in self:
            record.owner_id = "{},{}".format(record.model, record.res_id)

    @api.multi
    def _inverse_owner_id(self):
        """Store the owner according to the model and ID."""
        for record in self.filtered('owner_id'):
            record.model = record.owner_id._name
            record.res_id = record.owner_id.id

    @api.multi
    @api.depends("property_id.field_type", "field_name", "value_str",
                 "value_int", "value_float", "value_bool", "value_id")
    def _compute_value(self):
        """Get the value as a string, from the original field."""
        for s in self:
            if s.field_type == "id":
                s.value = s.value_id.display_name
            elif s.field_type == "bool":
                s.value = _("Yes") if s.value_bool else _("No")
            else:
                s.value = getattr(s, s.field_name, False)

    @api.multi
    def _inverse_value(self):
        """Write the value correctly converted in the typed field."""
        for record in self:
            if (record.field_type == "id" and
                    record.value == record.value_id.display_name):
                # Avoid another search that can return a different value
                continue
            record[record.field_name] = self._transform_value(
                record.value, record.field_type, record.property_id,
            )

    @api.constrains("property_id", "value_str", "value_int", "value_float")
    def _check_min_max_limits(self):
        """Ensure value falls inside the property's stablished limits."""
        minimum, maximum = self.property_id.minimum, self.property_id.maximum
        if minimum <= maximum:
            value = self[self.field_name]
            if not value:
                # This is a job for :meth:`.~_check_required`
                return
            if self.field_type == "str":
                number = len(self.value_str)
                message = _(
                    "Length for %(prop)s is %(val)s, but it should be "
                    "between %(min)d and %(max)d.")
            elif self.field_type in {"int", "float"}:
                number = value
                if self.field_type == "int":
                    message = _(
                        "Value for %(prop)s is %(val)s, but it should be "
                        "between %(min)d and %(max)d.")
                else:
                    message = _(
                        "Value for %(prop)s is %(val)s, but it should be "
                        "between %(min)f and %(max)f.")
            else:
                return
            if not minimum <= number <= maximum:
                raise ValidationError(message % {
                    "prop": self.property_id.display_name,
                    "val": number,
                    "min": minimum,
                    "max": maximum,
                })

    @api.multi
    @api.onchange("property_id")
    def _onchange_property_set_default_value(self):
        """Load default value for this property."""
        for record in self:
            if not record.value and record.property_id.default_value:
                record.value = record.property_id.default_value

    @api.onchange('value')
    def _onchange_value(self):
        """Inverse function is not launched after writing, so we need to
        trigger it right now."""
        self._inverse_value()

    @api.model
    def _transform_value(self, value, format_, properties=None):
        """Transforms a text value to the expected format.

        :param str/bool value:
            Custom value in raw string.

        :param str format_:
            Target conversion format for the value. Must be available among
            ``custom.info.property`` options.

        :param recordset properties:
            Useful when :param:`format_` is ``id``, as it helps to ensure the
            option is available in these properties. If :param:`format_` is
            ``id`` and :param:`properties` is ``None``, no transformation will
            be made for :param:`value`.
        """
        if not value:
            value = False
        elif format_ == "id" and properties:
            value = self.env["custom.info.option"].search([
                ("property_ids", "in", properties.ids),
                ("name", "ilike", u"%{}%".format(value)),
            ], limit=1)
        elif format_ == "bool":
            value = value.strip().lower() not in {
                "0", "false", "", "no", "off", _("No").lower()}
        elif format_ not in {"str", "id"}:
            value = safe_eval("{!s}({!r})".format(format_, value))
        return value

    @api.model
    def _search_value(self, operator, value):
        """Search from the stored field directly."""
        options = (
            o[0] for o in
            self.property_id._fields["field_type"]
            .get_description(self.env)["selection"])
        domain = []
        for fmt in options:
            try:
                _value = (self._transform_value(value, fmt)
                          if not isinstance(value, list) else
                          [self._transform_value(v, fmt) for v in value])
            except ValueError:
                # If you are searching something that cannot be casted, then
                # your property is probably from another type
                continue
            domain += [
                "&",
                ("field_type", "=", fmt),
                ("value_" + fmt, operator, _value),
            ]
        return ["|"] * (int(len(domain) / 3) - 1) + domain
