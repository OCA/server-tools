# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import ast

from odoo import api, fields, models

from .base import disable_changeset


class RecordChangeset(models.Model):
    _name = "record.changeset"
    _description = "Record Changeset"
    _order = "date desc"
    _rec_name = "date"

    model = fields.Char(index=True, required=True, readonly=True)
    res_id = fields.Many2oneReference(
        string="Record ID",
        index=True,
        readonly=True,
        model_field="model",
    )
    parent_model = fields.Char(string="Parent model", index=True)
    parent_id = fields.Integer(string="Parent", index=True)
    raw_changes = fields.Text(string="Raw changes")
    raw_changes_html = fields.Html(compute="_compute_raw_changes_html")
    change_ids = fields.One2many(
        comodel_name="record.changeset.change",
        inverse_name="changeset_id",
        string="Changes",
        readonly=True,
    )
    date = fields.Datetime(
        string="Modified on", default=fields.Datetime.now(), index=True, readonly=True
    )
    modified_by_id = fields.Many2one(
        "res.users", default=lambda self: self.env.user, readonly=True
    )
    action = fields.Selection(
        selection=[("create", "Add"), ("write", "Update"), ("unlink", "Remove")],
        default="write",
        string="Action",
    )
    state = fields.Selection(
        compute="_compute_state",
        selection=[("draft", "Pending"), ("done", "Done")],
        default="draft",
        store=True,
    )
    note = fields.Text()
    source = fields.Reference(
        string="Source of the change", selection="_reference_models", readonly=True
    )
    company_id = fields.Many2one("res.company")
    record_id = fields.Reference(
        selection="_reference_models", compute="_compute_resource_record", readonly=True
    )
    rule_id = fields.Many2one(
        comodel_name="changeset.field.rule",
        compute="_compute_rule_id",
        store=True,
    )

    @api.depends("action", "raw_changes")
    def _compute_raw_changes_html(self):
        """Create an html content to show the data to be validated and to be able
        to apopulate it."""
        allowed_field_types = (
            "boolean",
            "char",
            "date",
            "datetime",
            "float",
            "integer",
            "monetary",
            "selection",
            "text",
        )
        _self = self.filtered(lambda x: x.action == "create" and x.raw_changes)
        for item in _self:
            values = ast.literal_eval(item.raw_changes)
            field_name = list(values.keys())[0]
            final_values = values[field_name][0][2]
            raw_changes_html = ""
            model = self.env["ir.model"].sudo().search([("model", "=", item.model)])
            for key in list(final_values.keys()):
                field = model.field_id.filtered(lambda x: x.name == key)
                if field and field.ttype in allowed_field_types:
                    field_value = final_values[key]
                    if field_value or (not field_value and field.ttype == "boolean"):
                        raw_changes_html += "<p><b>%s</b>: %s</p>" % (
                            field.field_description,
                            field_value,
                        )
            item.raw_changes_html = raw_changes_html
        for item in self - _self:
            item.raw_changes_html = item.raw_changes_html

    @api.depends("model", "res_id")
    def _compute_resource_record(self):
        for changeset in self:
            changeset.record_id = "{},{}".format(changeset.model, changeset.res_id or 0)

    @api.model
    def _reference_models(self):
        models = self.env["ir.model"].sudo().search([])
        return [(model.model, model.name) for model in models]

    @api.depends("change_ids", "change_ids.state")
    def _compute_state(self):
        for rec in self.filtered(lambda x: x.change_ids):
            changes = rec.mapped("change_ids")
            if all(change.state in ("done", "cancel") for change in changes):
                rec.state = "done"
            else:
                rec.state = "draft"

    @api.depends("change_ids")
    def _compute_rule_id(self):
        for item in self.filtered(lambda x: x.change_ids):
            item.rule_id = fields.first(item.change_ids).rule_id

    @api.model
    def get_changeset_changes_one2many(self, model, res_id):
        fields = [
            "model",
            "res_id",
            "action",
            "raw_changes",
        ]
        domain = [
            ("parent_model", "=", model),
            ("parent_id", "=", res_id),
            ("state", "=", "draft"),
            ("action", "in", ("create", "unlink")),
        ]
        items = self.search_read(domain, fields)
        for item in items:
            item["raw_changes"] = ast.literal_eval(item["raw_changes"])
        return items

    def name_get(self):
        result = []
        for changeset in self:
            if changeset.record_id:
                name = "{} ({})".format(
                    changeset.date, changeset.record_id.display_name
                )
            else:
                name = "{} ({}) (New)".format(changeset.date, changeset.model)
            result.append((changeset.id, name))
        return result

    def apply(self):
        for item in self.filtered(lambda x: x.state == "draft"):
            if item.action == "create":
                item._apply_create()
            elif item.action == "write":
                item._apply_write()
            else:
                item._apply_unlink()

    def _apply_create(self):
        """Create for example a purchase.order.line record if there is an existing
        changeset rule will not create it, it will have created a changeset
        (with the raw_changes) and as many changes as subfields set (or all fields).
        To apply the change correctly, it will be necessary to write() in the parent
        model and save new id just created.
        Example: purchase_order.write({"order_line": [[0, 0, {"name": "test"}]]})."""
        if not self.parent_model or not self.parent_id or not self.raw_changes:
            raise UserError(_("Not applicable, missing data."))
        parent_record = self.env[self.parent_model].browse(self.parent_id)
        values = ast.literal_eval(self.raw_changes)
        field_name = list(values.keys())[0]
        old_values = parent_record[field_name]
        parent_record.with_context(__no_changeset=disable_changeset).write(values)
        new_value = parent_record[field_name] - old_values
        self.res_id = new_value.id
        self.state = "done"

    def _apply_write(self):
        self.with_context(skip_pending_status_check=True).mapped("change_ids").apply()

    def _apply_unlink(self):
        """Deleting for example a purchase.order.line record if a changeset rule exists
        would not delete it. A changeset would have been created (without changes) with
        the delete flag.
        The corresponding record will be deleted and set as done."""
        self.record_id.unlink()
        self.state = "done"

    def _set_changes_state(self, state):
        self.with_context(skip_pending_status_check=True).mapped("change_ids").write(
            {"state": state}
        )

    def cancel(self):
        """Cancel process will work as follows:
        - Create: Will set all changes as cancel (without actually applying any changes).
        - Write: Will set all corresponding changes.
        - Unlink: Will set the changeset as cancel (without changes)."""
        for item in self.filtered(lambda x: x.state == "draft"):
            if item.action == "create":
                item.state = "done"
            elif item.action == "write":
                item.with_context(skip_pending_status_check=True).mapped(
                    "change_ids"
                ).cancel()
            else:
                item.state = "done"

    # flake8: noqa: C901 (is too complex)
    @api.model
    def add_changeset(self, record, values, create=False):
        """Add a changeset on a record

        By default, when a record is modified by a user or by the
        system, the the changeset will follow the rules configured for
        the global rules.

        A caller should pass the following keys in the context:

        * ``__changeset_rules_source_model``: name of the model which
          asks for the change
        * ``__changeset_rules_source_id``: id of the record which asks
        for the change

        When the source model and id are not defined, the current user
        is considered as the origin of the change.

        Should be called before the execution of ``write`` on the record
        so we can keep track of the existing value and also because the
        returned values should be used for ``write`` as some of the
        values may have been removed.

        :param values: the values being written on the record
        :type values: dict
        :param create: in create mode, no check is made to see if the field
        value consitutes a change.
        :type creatie: boolean

        :returns: dict of values that should be wrote on the record
        (fields with a 'Validate' or 'Never' rule are excluded)

        """
        record.ensure_one()

        source_model = self.env.context.get("__changeset_rules_source_model")
        source_id = self.env.context.get("__changeset_rules_source_id")
        if not source_model:
            # if the changes source is not defined, log the user who
            # made the change
            source_model = "res.users"
        if not source_id:
            source_id = self.env.uid
        if source_model and source_id:
            source = "{},{}".format(source_model, source_id)
        else:
            source = False

        changeset_model = self.env["record.changeset"]
        change_model = self.env["record.changeset.change"]
        write_values = values.copy()
        changes = []
        rules = self.env["changeset.field.rule"].get_rules(
            source_model_name=source_model, record_model_name=record._name
        )
        for field in values:
            rule = rules.get(field)
            if (
                not rule
                or not rule._evaluate_expression(record)
                or (create and not values[field])
            ):
                continue
            if field in values:
                if not create and not change_model._has_field_changed(
                    record, field, values[field]
                ):
                    continue
            if rule.field_id.ttype == "one2many":
                write_values.pop(field)
                # Changes related to the one2many (create changeset and changes)
                child_model = self.env[rule.field_relation]
                for [command, child_res_id, child_vals] in values[field]:
                    if command in (0, 1, 2):
                        child_record = child_model
                        if child_res_id and isinstance(child_res_id, int):
                            child_record = child_model.browse(child_res_id)
                        # Prepare changes only to update (command=1)
                        child_changes = False
                        if command == 1:
                            child_changes = self._prepare_changes_vals_from_values(
                                child_record, child_vals, rule
                            )
                        # create changeset from child record
                        if child_changes or command in (0, 2):
                            child_changeset_vals = self._prepare_changeset_vals(
                                child_changes, child_record, source
                            )
                            if command == 0:
                                changeset_action = "create"
                                child_res_id = 0
                            elif command == 1:
                                changeset_action = "write"
                            elif command == 2:
                                changeset_action = "unlink"
                            child_changeset_vals.update(
                                {
                                    "parent_id": record.id,
                                    "parent_model": record._name,
                                    "action": changeset_action,
                                    "raw_changes": {
                                        field: [[command, child_res_id, child_vals]]
                                    },
                                }
                            )
                            # Set rule_id (change_ids not set) to set summary review fine
                            if changeset_action == "create":
                                child_changeset_vals.update(rule_id=rule.id)
                            if self._allow_create_changeset(child_changeset_vals):
                                # As there are no changes, it is not possible to know
                                # the rule that triggered it.
                                # base_changeset_tier_validation module needs to know
                                # the rule to create or not a review.
                                changeset_model.with_context(
                                    changeset_rule=rule
                                ).create(child_changeset_vals)
            else:
                change, pop_value = change_model._prepare_changeset_change(
                    record,
                    rule,
                    field,
                    values[field],
                    create=create,
                )
                if pop_value:
                    write_values.pop(field)
                    if create:
                        # overwrite with null value for new records
                        write_values[field] = (
                            # but create some default for required text fields
                            record._fields[field].required
                            and record._fields[field].type in ("char", "text")
                            and "/"
                            or record._fields[field].null(record)
                        )
                changes.append(change)
        if changes:
            changeset_vals = self._prepare_changeset_vals(changes, record, source)
            changeset_model.create(changeset_vals)
        return write_values

    def _allow_create_changeset(self, vals):
        """Check if it is necessary to create the changeset or not.
        It will only apply if it has parent_id and parent_model and in create or delete.
        The creation will be avoided if there is already a linked changeset without done.
        It should be avoided to create a new changeset to delete a line that already has
        a changeset or to create a new changeset to add a line that already has the same
        changeset."""
        if vals.get("action"):
            action = vals["action"]
            if action == "unlink":
                record = self.env[vals["model"]].browse(vals["res_id"])
                if any(
                    x.action == action and x.state == "draft"
                    for x in record.changeset_ids
                ):
                    return False
            elif action == "create" and vals.get("raw_changes"):
                parent_model = self.env[vals["parent_model"]].browse(vals["parent_id"])
                if any(
                    x.action == action
                    and x.state == "draft"
                    and ast.literal_eval(x.raw_changes) == vals["raw_changes"]
                    for x in parent_model.child_changeset_ids
                ):
                    return False

        return True

    def _prepare_changes_vals_from_values(self, record, vals, rule):
        """Set all the changes of the indicated vals according to the subfields
        of the rule related to the one2many field."""
        change_model = self.env["record.changeset.change"]
        changes = []
        if not vals:
            return changes
        for subfield in rule._get_all_subfields():
            if subfield.name in vals:
                change, _pop_value = change_model._prepare_changeset_change(
                    record,
                    rule,
                    subfield.name,
                    vals[subfield.name],
                )
                if change:
                    changes.append(change)
        return changes

    @api.model
    def _prepare_changeset_vals(self, changes, record, source):
        has_company = "company_id" in self.env[record._name]._fields
        has_company = has_company and record.company_id
        company = record.company_id if has_company else self.env.company
        return {
            # newly created records are passed as newid records with the id in ref
            "res_id": record.id or record.id.ref if record else False,
            "model": record._name,
            "company_id": company.id,
            "change_ids": [(0, 0, vals) for vals in changes] if changes else False,
            "date": fields.Datetime.now(),
            "source": source,
        }
