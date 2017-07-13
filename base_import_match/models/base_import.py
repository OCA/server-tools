# -*- coding: utf-8 -*-
# Copyright 2016 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# Copyright 2016 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models
from openerp import SUPERUSER_ID  # TODO remove in v10


class BaseImportMatch(models.Model):
    _name = "base_import.match"
    _description = "Deduplicate settings prior to CSV imports."
    _order = "sequence, name"

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
        domain=[("transient", "=", False)],
        help="In this model you will apply the match.")
    model_name = fields.Char(
        related="model_id.model",
        store=True,
        index=True)
    field_ids = fields.One2many(
        comodel_name="base_import.match.field",
        inverse_name="match_id",
        string="Fields",
        required=True,
        help="Fields that will define an unique key.")

    @api.multi
    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.field_ids.unlink()

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
            s.name = u"{}: {}".format(
                s.model_id.display_name,
                " + ".join(
                    s.field_ids.mapped(
                        lambda r: (
                            (u"{} ({})" if r.conditional else u"{}").format(
                                r.field_id.name,
                                r.imported_value)))))

    @api.model
    def _match_find(self, model, converted_row, imported_row):
        """Find a update target for the given row.

        This will traverse by order all match rules that can be used with the
        imported data, and return a match for the first rule that returns a
        single result.

        :param openerp.models.Model model:
            Model object that is being imported.

        :param dict converted_row:
            Row converted to Odoo api format, like the 3rd value that
            :meth:`openerp.models.Model._convert_records` returns.

        :param dict imported_row:
            Row as it is being imported, in format::

                {
                    "field_name": "string value",
                    "other_field": "True",
                    ...
                }

        :return openerp.models.Model:
            Return a dataset with one single match if it was found, or an
            empty dataset if none or multiple matches were found.
        """
        # Get usable rules to perform matches
        usable = self._usable_for_load(model._name, converted_row.keys())

        # Traverse usable combinations
        for combination in usable:
            combination_valid = True
            domain = list()

            for field in combination.field_ids:
                # Check imported value if it is a conditional field
                if field.conditional:
                    # Invalid combinations are skipped
                    if imported_row[field.name] != field.imported_value:
                        combination_valid = False
                        break

                domain.append((field.name, "=", converted_row[field.name]))

            if not combination_valid:
                continue

            match = model.search(domain)

            # When a single match is found, stop searching
            if len(match) == 1:
                return match

        # Return an empty match if none or multiple was found
        return model

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

            # Data conversion to ORM format
            import_fields = map(models.fix_import_export_id_paths, fields)
            converted_data = self._convert_records(
                self._extract_records(import_fields, data))

            # Mock Odoo to believe the user is importing the ID field
            if "id" not in fields:
                fields.append("id")
                import_fields.append(["id"])

            # Needed to match with converted data field names
            clean_fields = [f[0] for f in import_fields]

            for dbid, xmlid, record, info in converted_data:
                row = dict(zip(clean_fields, data[info["record"]]))
                match = self

                if xmlid:
                    # Skip rows with ID, they do not need all this
                    row["id"] = xmlid
                elif dbid:
                    # Find the xmlid for this dbid
                    match = self.browse(dbid)
                else:
                    # Store records that match a combination
                    match = self.env["base_import.match"]._match_find(
                        self, record, row)

                # Give a valid XMLID to this row if a match was found
                row["id"] = (match._BaseModel__export_xml_id()
                             if match else row.get("id", u""))

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


class BaseImportMatchField(models.Model):
    _name = "base_import.match.field"
    _description = "Field import match definition"

    name = fields.Char(
        related="field_id.name")
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        required=True,
        ondelete="cascade",
        domain="[('model_id', '=', model_id)]",
        help="Field that will be part of an unique key.")
    match_id = fields.Many2one(
        comodel_name="base_import.match",
        string="Match",
        ondelete="cascade",
        required=True)
    model_id = fields.Many2one(
        related="match_id.model_id")
    conditional = fields.Boolean(
        help="Enable if you want to use this field only in some conditions.")
    imported_value = fields.Char(
        help="If the imported value is not this, the whole matching rule will "
             "be discarded. Be careful, this data is always treated as a "
             "string, and comparison is case-sensitive so if you set 'True', "
             "it will NOT match '1' nor 'true', only EXACTLY 'True'.")

    @api.multi
    @api.onchange("field_id", "match_id", "conditional", "imported_value")
    def _onchange_match_id_name(self):
        """Update match name."""
        self.mapped("match_id")._compute_name()
