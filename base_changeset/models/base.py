# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.tools import config


class Base(models.AbstractModel):
    _inherit = "base"

    changeset_ids = fields.One2many(
        comodel_name="record.changeset",
        compute="_compute_changeset_ids",
        string="Changesets",
    )
    changeset_change_ids = fields.One2many(
        comodel_name="record.changeset.change",
        compute="_compute_changeset_ids",
        string="Changeset Changes",
    )
    count_pending_changesets = fields.Integer(
        compute="_compute_count_pending_changesets"
    )
    count_pending_changeset_changes = fields.Integer(
        compute="_compute_count_pending_changesets"
    )

    def _compute_changeset_ids(self):
        model_name = self._name
        for record in self:
            changesets = self.env["record.changeset"].search(
                [("model", "=", model_name), ("res_id", "=", record.id)]
            )
            record.changeset_ids = changesets
            record.changeset_change_ids = changesets.mapped("change_ids")

    def _compute_count_pending_changesets(self):
        model_name = self._name
        if model_name in self.models_to_track_changeset():
            for rec in self:
                changesets = rec.changeset_ids.filtered(
                    lambda rev: rev.state == "draft"
                    and rev.res_id == rec.id
                    and rev.model == model_name
                )
                changes = changesets.mapped("change_ids")
                changes = changes.filtered(
                    lambda c: c.state in c.get_pending_changes_states()
                )
                rec.count_pending_changesets = len(changesets)
                rec.count_pending_changeset_changes = len(changes)
        else:
            for rec in self:
                rec.count_pending_changesets = 0.0
                rec.count_pending_changeset_changes = 0.0

    @api.model
    def models_to_track_changeset(self):
        """Models to be tracked for changes
        :args:
        :returns: list of models
        """
        models = self.env["changeset.field.rule"].search([]).mapped("model_id.model")
        if config["test_enable"] and self.env.context.get("test_record_changeset"):
            if "res.partner" not in models:
                models += ["res.partner"]  # Used in tests
        return models

    def write(self, values):
        if self.env.context.get("__no_changeset"):
            return super().write(values)

        # To avoid conflicts with tests of other modules
        if config["test_enable"] and not self.env.context.get("test_record_changeset"):
            return super().write(values)

        if self._name not in self.models_to_track_changeset():
            return super().write(values)

        for record in self:
            local_values = self.env["record.changeset"].add_changeset(record, values)
            super(Base, record).write(local_values)
        return self

    def action_record_changeset_change_view(self):
        self.ensure_one()
        res = {
            "type": "ir.actions.act_window",
            "res_model": "record.changeset.change",
            "view_mode": "tree",
            "views": [
                [
                    self.env.ref("base_changeset.view_record_changeset_change_tree").id,
                    "list",
                ]
            ],
            "context": self.env.context,
            "name": _("Record Changes"),
            "search_view_id": [
                self.env.ref("base_changeset.view_record_changeset_change_search").id,
                "search",
            ],
        }
        record_id = self.env.context.get("search_default_record_id")
        if record_id:
            res.update(
                {
                    "domain": [
                        ("model", "=", self._name),
                        ("changeset_id.res_id", "=", record_id),
                    ]
                }
            )
        return res

    @api.model
    def _fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super()._fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        to_track_changeset = self._name in self.models_to_track_changeset()
        button_label = _("Changes")
        if to_track_changeset and view_type == "form" and self.user_can_see_changeset:
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//div[@name='button_box']"):
                xml_field = etree.Element(
                    "field",
                    {
                        "name": "count_pending_changeset_changes",
                        "string": button_label,
                        "widget": "statinfo",
                    },
                )
                xml_button = etree.Element(
                    "button",
                    {
                        "type": "object",
                        "name": "action_record_changeset_change_view",
                        "icon": "fa-code-fork",
                        "context": "{'search_default_draft': 1, "
                        "'search_default_record_id': active_id}",
                    },
                )
                xml_button.set(
                    "attrs",
                    str({"invisible": [("count_pending_changeset_changes", "=", 0)]}),
                )
                xml_button.insert(0, xml_field)
                node.insert(0, xml_button)
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    def user_can_see_changeset(self):
        is_superuser = self.env.is_superuser()
        has_changeset_group = self.user_has_groups(
            "base_changeset.group_changeset_user"
        )
        return is_superuser or has_changeset_group
