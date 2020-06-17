# Copyright 2015-2017 Camptocamp SA
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RecordChangeset(models.Model):
    _name = "record.changeset"
    _description = "Record Changeset"
    _order = "date desc"
    _rec_name = "date"

    model = fields.Char(index=True, required=True, readonly=True)
    res_id = fields.Many2oneReference(
        string="Record ID",
        index=True,
        required=True,
        readonly=True,
        model_field="model",
    )
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
    state = fields.Selection(
        compute="_compute_state",
        selection=[("draft", "Pending"), ("done", "Done")],
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
        for rec in self:
            changes = rec.mapped("change_ids")
            if all(change.state in ("done", "cancel") for change in changes):
                rec.state = "done"
            else:
                rec.state = "draft"

    def name_get(self):
        result = []
        for changeset in self:
            name = "{} ({})".format(changeset.date, changeset.record_id.name)
            result.append((changeset.id, name))
        return result

    def apply(self):
        self.with_context(skip_pending_status_check=True).mapped("change_ids").apply()

    def cancel(self):
        self.with_context(skip_pending_status_check=True).mapped("change_ids").cancel()

    @api.model
    def add_changeset(self, record, values):
        """ Add a changeset on a record

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

        change_model = self.env["record.changeset.change"]
        write_values = values.copy()
        changes = []
        rules = self.env["changeset.field.rule"].get_rules(
            source_model_name=source_model, record_model_name=record._name
        )
        for field in values:
            rule = rules.get(field)
            if not rule:
                continue
            if field in values:
                if not change_model._has_field_changed(record, field, values[field]):
                    continue
            change, pop_value = change_model._prepare_changeset_change(
                record, rule, field, values[field]
            )
            if pop_value:
                write_values.pop(field)
            changes.append(change)
        if changes:
            changeset_vals = self._prepare_changeset_vals(changes, record, source)
            self.env["record.changeset"].create(changeset_vals)
        return write_values

    @api.model
    def _prepare_changeset_vals(self, changes, record, source):
        has_company = "company_id" in self.env[record._name]._fields
        has_company = has_company and record.company_id
        company = record.company_id if has_company else self.env.company
        return {
            "res_id": record.id,
            "model": record._name,
            "company_id": company.id,
            "change_ids": [(0, 0, vals) for vals in changes],
            "date": fields.Datetime.now(),
            "source": source,
        }
