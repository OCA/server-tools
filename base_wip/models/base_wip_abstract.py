# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models, tools
from odoo.osv.orm import setup_modifiers

from .base_wip import display_time


class BaseWipAbstract(models.AbstractModel):
    _name = "base.wip.abstract"
    _description = "Base Wip Abstract"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        model_view = super(BaseWipAbstract, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )

        if view_type == "form":
            try:
                wip_view = self.env.ref("base_wip.base_wip_abstract_form_view")
                wip_arch = etree.fromstring(wip_view["arch"])

                page_node = wip_arch.xpath("//page[@name='wip_page']")[0]

                doc = etree.fromstring(model_view.get("arch"))

                # Replace page
                doc_page_node = doc.xpath("//notebook")[0]
                for n in page_node.getiterator():
                    setup_modifiers(n)

                doc_page_node.append(page_node)
                model_view["arch"] = etree.tostring(doc, encoding="unicode")
            except Exception:
                return model_view

        return model_view

    @api.depends("wip_ids")
    def _compute_time(self):
        for record in self:
            lead_time = sum(
                record.wip_ids.filtered(lambda x: not x.wip_state == "done").mapped(
                    "lead_time_seconds"
                )
            )
            cycle_time = sum(
                record.wip_ids.filtered(
                    lambda x: x.wip_state in ("open", "pending")
                ).mapped("lead_time_seconds")
            )
            reaction_time = sum(
                record.wip_ids.filtered(lambda x: x.wip_state == "draft").mapped(
                    "lead_time_seconds"
                )
            )
            logged_time = sum(
                record.wip_ids.filtered(lambda x: x.wip_state == "open").mapped(
                    "lead_time_seconds"
                )
            )

            record.logged_time_float = logged_time
            record.logged_time = display_time(logged_time, 5)

            record.lead_time_float = lead_time
            record.lead_time = display_time(lead_time, 5)

            record.cycle_time_float = cycle_time
            record.cycle_time = display_time(cycle_time, 5)

            record.reaction_time_float = reaction_time
            record.reaction_time = display_time(reaction_time, 5)

    def _compute_wip_ids(self):
        for record in self:
            record.wip_ids = record.wip_ids.search(
                [("model_id", "=", record._name), ("res_id", "=", record.id)]
            )

    wip_ids = fields.One2many(comodel_name="base.wip", compute="_compute_wip_ids")

    lead_time_float = fields.Float(
        compute="_compute_time",
    )

    lead_time = fields.Char(
        compute="_compute_time",
    )

    cycle_time_float = fields.Float(
        compute="_compute_time",
    )

    cycle_time = fields.Char(
        compute="_compute_time",
    )

    reaction_time_float = fields.Float(
        compute="_compute_time",
    )

    reaction_time = fields.Char(
        compute="_compute_time",
    )

    logged_time_float = fields.Float(
        compute="_compute_time",
    )

    logged_time = fields.Char(
        compute="_compute_time",
    )

    @api.model
    def create(self, vals):
        result = super(BaseWipAbstract, self).create(vals)
        result.wip_ids.start(
            model_id=self._name,
            res_id=result.id,
            wip_state=vals.get("wip_state", "draft"),
        )
        return result

    def write(self, vals):
        if vals.get("wip_state"):
            self.wip_ids.stop()
            self.wip_ids.start(
                model_id=self._name, res_id=self.id, wip_state=vals.get("wip_state")
            )
        return super(BaseWipAbstract, self).write(vals)


class BaseWipReport(models.Model):
    _name = "base.wip.report"
    _auto = False

    model_id = fields.Many2one(comodel_name="ir.model")
    res_id = fields.Integer(
        string="Resource ID",
        index=True,
    )
    wip_state = fields.Selection(
        selection=[
            ("draft", "New"),
            ("open", "In Progress"),
            ("pending", "Pending"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
            ("exception", "Exception"),
        ],
        string="State",
        index=True,
    )

    reference_id = fields.Reference(
        string="Record", selection=[], compute="_compute_time"
    )

    lead_time_float = fields.Float(
        compute="_compute_time",
    )

    lead_time = fields.Char(
        compute="_compute_time",
    )

    cycle_time_float = fields.Float(
        compute="_compute_time",
    )

    cycle_time = fields.Char(
        compute="_compute_time",
    )

    reaction_time_float = fields.Float(
        compute="_compute_time",
    )

    reaction_time = fields.Char(
        compute="_compute_time",
    )

    logged_time_float = fields.Float(
        compute="_compute_time",
    )

    logged_time = fields.Char(
        compute="_compute_time",
    )

    @api.depends("model_id", "res_id")
    def _compute_time(self):
        for record in self:
            record.reference_id = "%s,%s" % (record.model_id.model, record.res_id)
            wip_ids = record.env["base.wip"].search(
                [("model_id", "=", record.model_id.id), ("res_id", "=", record.res_id)]
            )
            lead_time = sum(
                wip_ids.filtered(lambda x: not x.wip_state == "done").mapped(
                    "lead_time_seconds"
                )
            )
            cycle_time = sum(
                wip_ids.filtered(lambda x: x.wip_state in ("open", "pending")).mapped(
                    "lead_time_seconds"
                )
            )
            reaction_time = sum(
                wip_ids.filtered(lambda x: x.wip_state == "draft").mapped(
                    "lead_time_seconds"
                )
            )
            logged_time = sum(
                wip_ids.filtered(lambda x: x.wip_state == "open").mapped(
                    "lead_time_seconds"
                )
            )

            record.logged_time_float = logged_time
            record.logged_time = display_time(logged_time, 5)

            record.lead_time_float = lead_time
            record.lead_time = display_time(lead_time, 5)

            record.cycle_time_float = cycle_time
            record.cycle_time = display_time(cycle_time, 5)

            record.reaction_time_float = reaction_time
            record.reaction_time = display_time(reaction_time, 5)

    @api.multi
    def open_form(self):
        return {
            "type": "ir.actions.act_window",
            "name": self.reference_id.name,
            "view_type": "form",
            "view_mode": "form",
            "res_model": self.model_id.model,
            "res_id": self.res_id,
            "target": "current",
        }

    def init(self):
        """
        CRM Lead Report
        @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(self._cr, "base_wip_report")
        self._cr.execute(
            """
                CREATE OR REPLACE VIEW base_wip_report AS (
                with initial as (select
                    max(id) as id, res_id, model_id
                from base_wip
                group by res_id, model_id)
                select
                    id, res_id, model_id, wip_state
                from base_wip
                where id in (select id from initial)
                group by id, res_id, model_id, wip_state
                )"""
        )
