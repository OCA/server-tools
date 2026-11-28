# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

ACTION_CODE = "action = env['remote.odoo.export.wizard'].open_for(records)"
UNSUPPORTED_FIELD_TYPES = (
    "one2many",
    "many2many",
    "binary",
    "reference",
    "json",
)
SUPPORTED_STORED_FIELD_DOMAIN = (
    "[('model_id', '=', model_id), ('store', '=', True), "
    f"('ttype', 'not in', {list(UNSUPPORTED_FIELD_TYPES)})]"
)


class RemoteOdooMatchConfig(models.Model):
    _name = "remote.odoo.match.config"
    _description = "Remote Odoo Match Configuration"
    _rec_name = "model_id"

    model_id = fields.Many2one(
        "ir.model",
        required=True,
        ondelete="cascade",
        help="Local model exposed for remote export.",
    )
    model_name = fields.Char(related="model_id.model", store=True, index=True)
    use_external_id = fields.Boolean(
        default=True,
        help=(
            "If checked, the remote record is first looked up by External ID "
            "(ir.model.data). Falls back to match fields if no xmlid is set."
        ),
    )
    match_field_ids = fields.Many2many(
        "ir.model.fields",
        relation="remote_odoo_match_config_match_field_rel",
        column1="config_id",
        column2="field_id",
        domain=SUPPORTED_STORED_FIELD_DOMAIN,
        help="Fields used to look up the remote record when no External ID is set.",
    )
    export_field_ids = fields.Many2many(
        "ir.model.fields",
        relation="remote_odoo_match_config_export_field_rel",
        column1="config_id",
        column2="field_id",
        domain=SUPPORTED_STORED_FIELD_DOMAIN,
        help=(
            "Fields to send when CREATING the remote record. If empty, all "
            "stored writable scalar and many2one fields are sent."
        ),
    )
    update_field_ids = fields.Many2many(
        "ir.model.fields",
        relation="remote_odoo_match_config_update_field_rel",
        column1="config_id",
        column2="field_id",
        domain=SUPPORTED_STORED_FIELD_DOMAIN,
        help=(
            "Fields to send when UPDATING an existing remote record. If "
            "empty, the create field set is reused."
        ),
    )
    match_strategy = fields.Selection(
        [
            ("each_field_or", "Each field is an independent fallback"),
            ("all_fields_and", "All fields combined (compound key)"),
        ],
        default="each_field_or",
        required=True,
        help=(
            "How to combine match fields when looking up the remote record. "
            "'Each field' tries them one by one in order (first single-match "
            "wins) — use when fields are alternative keys. 'All fields' "
            "requires every field to match — use for compound keys."
        ),
    )
    operation = fields.Selection(
        [
            ("create_and_update", "Create and update"),
            ("create_only", "Create only"),
            ("update_only", "Update only"),
        ],
        default="create_and_update",
        required=True,
        help=(
            "Default behaviour proposed in the wizard. The wizard always "
            "lets the user override it for a given run."
        ),
    )
    recursive_match = fields.Boolean(
        help=(
            "When resolving a many2one field whose target has no External "
            "ID, look it up on the remote using the match fields configured "
            "for the target model. Avoids creating orphan relations."
        ),
    )
    action_id = fields.Many2one(
        "ir.actions.server",
        readonly=True,
        ondelete="set null",
        copy=False,
    )

    _sql_constraints = [
        (
            "model_id_uniq",
            "unique(model_id)",
            "There is already a remote export configuration for this model.",
        ),
    ]

    @api.constrains("use_external_id", "match_field_ids")
    def _check_match_keys(self):
        for record in self:
            if not record.use_external_id and not record.match_field_ids:
                raise ValidationError(
                    _(
                        "You must enable 'Use External ID' or specify at "
                        "least one match field."
                    )
                )

    def _action_vals(self):
        self.ensure_one()
        return {
            "name": _("Remote Export"),
            "model_id": self.model_id.id,
            "binding_model_id": self.model_id.id,
            "binding_view_types": "list,form",
            "state": "code",
            "code": ACTION_CODE,
        }

    def _sync_action(self):
        for record in self:
            vals = record._action_vals()
            if record.action_id:
                record.action_id.write(vals)
            else:
                record.action_id = self.env["ir.actions.server"].create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_action()
        return records

    def write(self, vals):
        res = super().write(vals)
        if "model_id" in vals:
            self._sync_action()
        return res

    def unlink(self):
        actions = self.mapped("action_id")
        res = super().unlink()
        actions.unlink()
        return res
