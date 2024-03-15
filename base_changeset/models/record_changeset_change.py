# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby
from operator import attrgetter

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .base import disable_changeset

# sentinel object to be sure that no empty value was passed to
# RecordChangesetChange._value_for_changeset
_NO_VALUE = object()


class RecordChangesetChange(models.Model):
    """Store the change of one field for one changeset on one record

    This model is composed of 3 sets of fields:

    * 'origin'
    * 'old'
    * 'new'

    The 'new' fields contain the value that needs to be validated.
    The 'old' field copies the actual value of the record when the
    change is either applied either canceled. This field is used as a storage
    place but never shown by itself.
    The 'origin' fields is a related field towards the actual values of
    the record until the change is either applied either canceled, past
    that it shows the 'old' value.
    The reason behind this is that the values may change on a record between
    the moment when the changeset is created and when it is applied.

    On the views, we show the origin fields which represent the actual
    record values or the old values and we show the new fields.

    The 'origin' and 'new_value_display' are displayed on
    the tree view where we need a unique of field, the other fields are
    displayed on the form view so we benefit from their widgets.

    """

    _name = "record.changeset.change"
    _description = "Record Changeset Change"
    _rec_name = "field_id"

    changeset_id = fields.Many2one(
        comodel_name="record.changeset",
        required=True,
        ondelete="cascade",
        readonly=True,
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    is_informative_change = fields.Boolean(
        compute="_compute_is_informative_change", store=True
    )
    field_name = fields.Char(related="field_id.name", readonly=True)
    field_type = fields.Selection(related="field_id.ttype", readonly=True)
    model = fields.Char(related="field_id.model", readonly=True, store=True)
    origin_value_display = fields.Char(
        string="Previous", compute="_compute_value_display"
    )
    new_value_display = fields.Char(string="New", compute="_compute_value_display")

    # Fields showing the origin record's value or the 'old' value if
    # the change is applied or canceled.
    origin_value_char = fields.Char(compute="_compute_origin_values", readonly=True)
    origin_value_date = fields.Date(compute="_compute_origin_values", readonly=True)
    origin_value_datetime = fields.Datetime(
        compute="_compute_origin_values", readonly=True
    )
    origin_value_float = fields.Float(compute="_compute_origin_values", readonly=True)
    origin_value_monetary = fields.Float(
        compute="_compute_origin_values", readonly=True
    )
    origin_value_integer = fields.Integer(
        compute="_compute_origin_values", readonly=True
    )
    origin_value_text = fields.Text(compute="_compute_origin_values", readonly=True)
    origin_value_boolean = fields.Boolean(
        compute="_compute_origin_values", readonly=True
    )
    origin_value_reference = fields.Reference(
        compute="_compute_origin_values", selection="_reference_models", readonly=True
    )

    # Fields storing the previous record's values (saved when the
    # changeset is applied)
    old_value_char = fields.Char(readonly=True)
    old_value_date = fields.Date(readonly=True)
    old_value_datetime = fields.Datetime(readonly=True)
    old_value_float = fields.Float(readonly=True)
    old_value_monetary = fields.Float(readonly=True)
    old_value_integer = fields.Integer(readonly=True)
    old_value_text = fields.Text(readonly=True)
    old_value_boolean = fields.Boolean(readonly=True)
    old_value_reference = fields.Reference(selection="_reference_models", readonly=True)

    # Fields storing the value applied on the record
    new_value_char = fields.Char(readonly=True)
    new_value_date = fields.Date(readonly=True)
    new_value_datetime = fields.Datetime(readonly=True)
    new_value_float = fields.Float(readonly=True)
    new_value_monetary = fields.Float(readonly=True)
    new_value_integer = fields.Integer(readonly=True)
    new_value_text = fields.Text(readonly=True)
    new_value_boolean = fields.Boolean(readonly=True)
    new_value_reference = fields.Reference(selection="_reference_models", readonly=True)

    state = fields.Selection(
        selection=[("draft", "Pending"), ("done", "Approved"), ("cancel", "Rejected")],
        required=True,
        default="draft",
        readonly=True,
    )
    record_id = fields.Reference(related="changeset_id.record_id")
    rule_id = fields.Many2one("changeset.field.rule", readonly=True)
    user_can_validate_changeset = fields.Boolean(
        compute="_compute_user_can_validate_changeset"
    )
    date = fields.Datetime(related="changeset_id.date")
    modified_by_id = fields.Many2one(related="changeset_id.modified_by_id")
    verified_on_date = fields.Datetime(string="Verified on", readonly=True)
    verified_by_id = fields.Many2one("res.users", readonly=True)

    @api.model
    def _reference_models(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    _suffix_to_types = {
        "char": ("char", "selection"),
        "date": ("date",),
        "datetime": ("datetime",),
        "float": ("float",),
        "monetary": ("monetary",),
        "integer": ("integer",),
        "text": ("text",),
        "boolean": ("boolean",),
        "reference": ("many2one",),
    }

    _type_to_suffix = {
        ftype: suffix for suffix, ftypes in _suffix_to_types.items() for ftype in ftypes
    }

    _origin_value_fields = ["origin_value_%s" % suffix for suffix in _suffix_to_types]
    _old_value_fields = ["old_value_%s" % suffix for suffix in _suffix_to_types]
    _new_value_fields = ["new_value_%s" % suffix for suffix in _suffix_to_types]
    _value_fields = _origin_value_fields + _old_value_fields + _new_value_fields

    @api.depends("changeset_id.res_id", "changeset_id.model")
    def _compute_origin_values(self):
        states = self.get_pending_changes_states()
        field_names = [
            field_name
            for field_name in self._fields.keys()
            if field_name.startswith("origin_value_")
            and field_name != "origin_value_display"
        ]
        for rec in self:
            field_name = rec.get_field_for_type(rec.field_id, "origin")
            for fname in field_names:
                if fname == field_name:
                    if rec.state in states:
                        value = rec.record_id[rec.field_id.name]
                    else:
                        old_field = rec.get_field_for_type(rec.field_id, "old")
                        value = rec[old_field]
                    setattr(rec, fname, value)
                else:
                    setattr(rec, fname, False)

    @api.depends("field_id", "model")
    def _compute_is_informative_change(self):
        for item in self:
            if item.model and item.field_id:
                model_field = self.env[item.model]._fields[item.field_id.name]
                item.is_informative_change = bool(
                    model_field.related or model_field.compute
                )
            else:
                item.is_informative_change = False

    @api.depends(lambda self: self._value_fields)
    def _compute_value_display(self):
        for rec in self:
            for prefix in ("origin", "new"):
                value = getattr(rec, "get_%s_value" % prefix)()
                if rec.field_id.ttype == "many2one" and value:
                    value = value.display_name
                setattr(rec, "%s_value_display" % prefix, value)

    @api.model
    def get_field_for_type(self, field, prefix):
        assert prefix in ("origin", "old", "new")
        field_type = self._type_to_suffix.get(field.ttype)
        if not field_type:
            raise NotImplementedError("field type %s is not supported" % field_type)
        return "{}_value_{}".format(prefix, field_type)

    def get_origin_value(self):
        self.ensure_one()
        field_name = self.get_field_for_type(self.field_id, "origin")
        return self[field_name]

    def get_new_value(self):
        self.ensure_one()
        field_name = self.get_field_for_type(self.field_id, "new")
        return self[field_name]

    def set_old_value(self):
        """Copy the value of the record to the 'old' field"""
        for change in self.filtered(lambda x: not x.is_informative_change):
            # copy the existing record's value for the history
            old_value_for_write = self._value_for_changeset(
                change.record_id, change.field_id.name
            )
            old_field_name = self.get_field_for_type(change.field_id, "old")
            change.write({old_field_name: old_value_for_write})

    def apply(self):
        """Apply the change on the changeset's record

        It is optimized thus that it makes only one write on the record
        per changeset if many changes are applied at once.
        """
        for change in self:
            if not change.user_can_validate_changeset:
                raise UserError(_("You don't have the rights to apply the changes."))
        changes_ok = self.browse()
        key = attrgetter("changeset_id")
        for changeset, changes in groupby(
            self.with_context(__no_changeset=disable_changeset).sorted(key=key), key=key
        ):
            values = {}
            for change in changes:
                if change.state in ("cancel", "done"):
                    continue

                if change.is_informative_change:
                    change._finalize_change_approval()
                else:
                    field = change.field_id
                    new_value = change.get_new_value()
                    value_for_write = change._convert_value_for_write(new_value)
                    values[field.name] = value_for_write

                    change.set_old_value()

                changes_ok |= change

            if not values:
                continue

            self._check_previous_changesets(changeset)

            changeset.record_id.with_context(__no_changeset=disable_changeset).write(
                values
            )

        changes_ok._finalize_change_approval()

    def _check_previous_changesets(self, changeset):
        if self.env.context.get("require_previous_changesets_done"):
            states = self.get_pending_changes_states()
            previous_changesets = self.env["record.changeset"].search(
                [
                    ("date", "<", changeset.date),
                    ("state", "in", states),
                    ("model", "=", changeset.model),
                    ("res_id", "=", changeset.res_id),
                ],
                limit=1,
            )
            if previous_changesets:
                raise UserError(
                    _(
                        "This change cannot be applied because a previous "
                        "changeset for the same record is pending.\n"
                        "Apply all the anterior changesets before applying "
                        "this one."
                    )
                )

    def cancel(self):
        """Reject the change"""
        for change in self:
            if not change.user_can_validate_changeset:
                raise UserError(_("You don't have the rights to reject the changes."))
        if any(change.state == "done" for change in self):
            raise UserError(_("This change has already be applied."))
        self.set_old_value()
        self._finalize_change_rejection()

    def _finalize_change_approval(self):
        self.write(
            {
                "state": "done",
                "verified_by_id": self.env.user.id,
                "verified_on_date": fields.Datetime.now(),
            }
        )

    def _finalize_change_rejection(self):
        self.write(
            {
                "state": "cancel",
                "verified_by_id": self.env.user.id,
                "verified_on_date": fields.Datetime.now(),
            }
        )

    @api.model
    def _has_field_changed(self, record, field, value):
        field_def = record._fields[field]
        current_value = field_def.convert_to_write(record[field], record)
        if not (current_value or value):
            return False
        return current_value != value

    def _convert_value_for_write(self, value):
        if not value:
            return value
        model = self.env[self.field_id.model_id.model]
        model_field_def = model._fields[self.field_id.name]
        return model_field_def.convert_to_write(value, self.record_id)

    @api.model
    def _value_for_changeset(self, record, field_name, value=_NO_VALUE):
        """Return a value from the record ready to write in a changeset field

        :param record: modified record
        :param field_name: name of the modified field
        :param value: if no value is given, it is read from the record
        """
        field_def = record._fields[field_name]
        if value is _NO_VALUE:
            # when the value is read from the record, we need to prepare
            # it for the write (e.g. extract .id from a many2one record)
            value = field_def.convert_to_write(record[field_name], record)
        if field_def.type == "many2one":
            # store as 'reference'
            comodel = field_def.comodel_name
            return "{},{}".format(comodel, value) if value else False
        else:
            return value

    @api.model
    def _prepare_changeset_change(self, record, rule, field_name, value, create=False):
        """Prepare data for a changeset change

        It returns a dict of the values to write on the changeset change
        and a boolean that indicates if the value should be popped out
        of the values to write on the model.

        :returns: dict of values, boolean
        """
        new_field_name = self.get_field_for_type(rule.field_id, "new")
        new_value = self._value_for_changeset(record, field_name, value=value)
        change = {
            new_field_name: new_value,
            "field_id": rule.field_id.id,
            "rule_id": rule.id,
        }
        if rule.action == "auto":
            change["state"] = "done"
            pop_value = False
        elif rule.action == "validate":
            change["state"] = "draft"
            pop_value = True  # change to apply manually
        elif rule.action == "never":
            change["state"] = "cancel"
            pop_value = True  # change never applied

        if create or change["state"] in ("cancel", "done"):
            # Normally the 'old' value is set when we use the 'apply'
            # button, but since we short circuit the 'apply', we
            # directly set the 'old' value here
            old_field_name = self.get_field_for_type(rule.field_id, "old")
            # get values ready to write as expected by the changeset
            # (for instance, a many2one is written in a reference
            # field)
            origin_value = self._value_for_changeset(
                record, field_name, value=False if create else _NO_VALUE
            )
            change[old_field_name] = origin_value

        return change, pop_value

    @api.model
    def get_fields_changeset_changes(self, model, res_id):
        fields = [
            "new_value_display",
            "origin_value_display",
            "field_name",
            "user_can_validate_changeset",
        ]
        states = self.get_pending_changes_states()
        domain = [
            ("changeset_id.model", "=", model),
            ("changeset_id.res_id", "=", res_id),
            ("state", "in", states),
        ]
        return self.search_read(domain, fields)

    def _compute_user_can_validate_changeset(self):
        is_superuser = self.env.is_superuser()
        has_group = self.user_has_groups("base_changeset.group_changeset_user")
        user_groups = self.env.user.groups_id
        for rec in self:
            can_validate = rec._is_change_pending() and (
                is_superuser
                or rec.rule_id.validator_group_ids & user_groups
                or has_group
            )
            if rec.rule_id.prevent_self_validation:
                can_validate = can_validate and rec.modified_by_id != self.env.user
            rec.user_can_validate_changeset = can_validate

    @api.model
    def get_pending_changes_states(self):
        return ["draft"]

    def _is_change_pending(self):
        self.ensure_one()
        skip_status_check = self.env.context.get("skip_pending_status_check")
        return skip_status_check or self.state in self.get_pending_changes_states()
