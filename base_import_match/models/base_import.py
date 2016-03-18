# -*- coding: utf-8 -*-
# © 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.exceptions import except_orm as ValueError  # TODO remove in v9
from openerp import SUPERUSER_ID  # TODO remove in v10


class BaseImportMatch(models.Model):
    _name = "base_import.match"
    _description = "Deduplicate settings prior to CSV imports."
    _order = "sequence, name"
    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Duplicated match!"),
    ]

    name = fields.Char(
        compute="_compute_name",
        store=True,
        index=True)
    sequence = fields.Integer(index=True)
    model_id = fields.Many2one(
        "ir.model",
        "Model",
        required=True,
        ondelete="cascade",
        domain=[("osv_memory", "=", False)],
        help="In this model you will apply the match.")
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        index=True)
    field_ids = fields.Many2many(
        "ir.model.fields",
        string="Fields",
        required=True,
        domain="[('model_id', '=', model_id)]",
        help="Fields that will define an unique key.")

    @api.multi
    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_ids = False

    @api.model
    def create(self, vals):
        """Wrap the model after creation."""
        result = super(BaseImportMatch, self).create(vals)
        self._load_autopatch(result.model_name)
        return result

    @api.multi
    def unlink(self):
        """Unwrap the model after deletion."""
        models = set(self.mapped("model_name"))
        result = super(BaseImportMatch, self).unlink()
        for model in models:
            self._load_autopatch(model)
        return result

    @api.multi
    def write(self, vals):
        """Wrap the model after writing."""
        result = super(BaseImportMatch, self).write(vals)

        if "model_id" in vals or "model_name" in vals:
            for s in self:
                self._load_autopatch(s.model_name)

        return result

    # TODO convert to @api.model_cr in v10
    def _register_hook(self, cr):
        """Autopatch on init."""
        models = set(
            self.browse(
                cr,
                SUPERUSER_ID,
                self.search(cr, SUPERUSER_ID, list()))
            .mapped("model_name"))
        for model in models:
            self._load_autopatch(cr, SUPERUSER_ID, model)

    @api.multi
    @api.depends("model_id", "field_ids")
    def _compute_name(self):
        """Automatic self-descriptive name for the setting records."""
        for s in self:
            s.name = "{}: {}".format(
                s.model_id.display_name,
                " + ".join(s.field_ids.mapped("display_name")))

    @api.model
    def _load_wrapper(self):
        """Create a new load patch method."""
        @api.model
        def wrapper(self, fields, data):
            """Try to identify rows by other pseudo-unique keys.

            It searches for rows that have no XMLID specified, and gives them
            one if any :attr:`~.field_ids` combination is found. With a valid
            XMLID in place, Odoo will understand that it must *update* the
            record instead of *creating* a new one.
            """
            newdata = list()

            # Mock Odoo to believe the user is importing the ID field
            if "id" not in fields:
                fields.append("id")

            # Needed to work with relational fields
            clean_fields = [
                models.fix_import_export_id_paths(f)[0] for f in fields]

            # Get usable rules to perform matches
            usable = self.env["base_import.match"]._usable_for_load(
                self._name, clean_fields)

            for row in (dict(zip(clean_fields, r)) for r in data):
                # All rows need an ID
                if "id" not in row:
                    row["id"] = u""

                # Skip rows with ID, they do not need all this
                elif row["id"]:
                    continue

                # Store records that match a combination
                match = self
                for combination in usable:
                    match |= self.search(
                        [(field.name, "=", row[field.name])
                         for field in combination.field_ids])

                    # When a single match is found, stop searching
                    if len(match) != 1:
                        break

                # Only one record should have been found
                try:
                    match.ensure_one()

                # You hit this because...
                # a. No match. Odoo must create a new record.
                # b. Multiple matches. No way to know which is the right
                #    one, so we let Odoo create a new record or raise
                #    the corresponding exception.
                # In any case, we must do nothing.
                except ValueError:
                    continue

                # Give a valid XMLID to this row
                row["id"] = match._BaseModel__export_xml_id()

                # Store the modified row, in the same order as fields
                newdata.append(tuple(row[f] for f in clean_fields))

            # Leave the rest to Odoo itself
            del data
            return wrapper.origin(self, fields, newdata)

        # Flag to avoid confusions with other possible wrappers
        wrapper.__base_import_match = True

        return wrapper

    @api.model
    def _load_autopatch(self, model_name):
        """[Un]apply patch automatically."""
        self._load_unpatch(model_name)
        if self.search([("model_name", "=", model_name)]):
            self._load_patch(model_name)

    @api.model
    def _load_patch(self, model_name):
        """Apply patch for :param:`model_name`'s load method.

        :param str model_name:
            Model technical name, such as ``res.partner``.
        """
        self.env[model_name]._patch_method(
            "load", self._load_wrapper())

    @api.model
    def _load_unpatch(self, model_name):
        """Apply patch for :param:`model_name`'s load method.

        :param str model_name:
            Model technical name, such as ``res.partner``.
        """
        model = self.env[model_name]

        # Unapply patch only if there is one
        try:
            if model.load.__base_import_match:
                model._revert_method("load")
        except AttributeError:
            pass

    @api.model
    def _usable_for_load(self, model_name, fields):
        """Return a set of elements usable for calling ``load()``.

        :param str model_name:
            Technical name of the model where you are loading data.
            E.g. ``res.partner``.

        :param list(str|bool) fields:
            List of field names being imported.
        """
        result = self
        available = self.search([("model_name", "=", model_name)])

        # Use only criteria with all required fields to match
        for record in available:
            if all(f.name in fields for f in record.field_ids):
                result += record

        return result
