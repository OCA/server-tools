# Copyright 2021 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource
from odoo.tools.safe_eval import safe_eval

CATEGORY_SELECTION = [
    ("required", "Required"),
    ("optional", "Optional"),
    ("no", "None"),
]


class RequestCategory(models.Model):
    _name = "request.category"
    _description = "Request Category"
    _order = "sequence"
    _check_company_auto = True
    _use_approver = True

    def _get_default_image(self):
        default_image_path = get_module_resource(
            "request_flow", "static/src/img", "checklist-svgrepo-com.svg"
        )
        return base64.b64encode(open(default_image_path, "rb").read())

    name = fields.Char(string="Name", translate=True, required=True)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        copy=False,
        required=True,
        index=True,
        default=lambda s: s.env.company,
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(string="Sequence")
    description = fields.Char(string="Description", translate=True)
    image = fields.Binary(string="Image", default=_get_default_image)
    has_date = fields.Selection(
        CATEGORY_SELECTION, string="Has Date", default="no", required=True
    )
    has_period = fields.Selection(
        CATEGORY_SELECTION, string="Has Period", default="no", required=True
    )
    has_quantity = fields.Selection(
        CATEGORY_SELECTION, string="Has Quantity", default="no", required=True
    )
    has_amount = fields.Selection(
        CATEGORY_SELECTION, string="Has Amount", default="no", required=True
    )
    has_reference = fields.Selection(
        CATEGORY_SELECTION,
        string="Has Reference",
        default="no",
        required=True,
        help="An additional reference that should be specified on the request.",
    )
    has_partner = fields.Selection(
        CATEGORY_SELECTION, string="Has Contact", default="no", required=True
    )
    has_location = fields.Selection(
        CATEGORY_SELECTION, string="Has Location", default="no", required=True
    )
    has_product = fields.Selection(
        CATEGORY_SELECTION,
        string="Has Product",
        default="no",
        required=True,
        help="Additional products that should be specified on the request.",
    )
    has_document = fields.Selection(
        CATEGORY_SELECTION,
        string="Has Documents",
        default="no",
        required=True,
    )
    has_child_request = fields.Selection(
        CATEGORY_SELECTION,
        string="Has Child Requests",
        default="no",
        required=True,
    )
    is_manager_approver = fields.Boolean(
        string="Employee's Manager",
        help="Automatically add the manager as approver on the request.",
    )
    request_to_validate_count = fields.Integer(
        "Number of request to validate",
        compute="_compute_request_to_validate_count",
    )
    automated_sequence = fields.Boolean(
        "Automated Sequence?",
        help="If checked, the Request will have an automated "
        "generated name based on the given code.",
    )
    sequence_code = fields.Char(string="Code")
    sequence_id = fields.Many2one(
        "ir.sequence", "Reference Sequence", copy=False, check_company=True
    )
    draft_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="Set to Draft Action",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "request.request"),
        ],
        help="Server action that can get executed after the request is set to draft",
    )
    approved_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="After Approved Action",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "request.request"),
        ],
        help="Server action that can get executed after the request is approved",
    )
    pending_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="After Submitted Action",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "request.request"),
        ],
        help="Server action that can get executed after the request is submitted",
    )
    refused_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="After Refused Action",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "request.request"),
        ],
        help="Server action that can get executed after the request is refused",
    )
    cancel_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="After Cancelled Action",
        domain=[
            ("usage", "=", "ir_actions_server"),
            ("model_id.model", "=", "request.request"),
        ],
        help="Server action that can get executed after the request is cancelled",
    )
    use_approver = fields.Boolean(compute="_compute_use_approver")
    context_overwrite = fields.Text(
        help="""
Valid dictionary to overwrite default context on New Request,
use env for self.env, i.e.,
{"default_amount": 100000,
 "default_location": "G2 Building, Bangkok",
 "default_requested_by": env.user.id}
        """
    )
    help = fields.Html(help="Explaination for a complex request operation.")
    has_child_doc = fields.Boolean(
        compute="_compute_has_child_doc",
        help="Checked, if the module was extened to have child documents",
    )
    child_doc_option_ids = fields.One2many(
        comodel_name="request.category.child.doc.option",
        inverse_name="category_id",
    )

    def _compute_use_approver(self):
        self.update({"use_approver": self._use_approver})

    def _compute_request_to_validate_count(self):
        domain = [
            ("state", "=", "pending"),
            ("approver_id", "=", self.env.user.id),
        ]
        request_data = self.env["request.request"].read_group(
            domain, ["category_id"], ["category_id"]
        )
        request_mapped_data = {
            data["category_id"][0]: data["category_id_count"] for data in request_data
        }
        for category in self:
            category.request_to_validate_count = request_mapped_data.get(category.id, 0)

    def _compute_has_child_doc(self):
        for rec in self:
            rec.has_child_doc = rec._has_child_doc()

    def _has_child_doc(self):
        self.ensure_one()
        return False

    @api.model
    def create(self, vals):
        if vals.get("automated_sequence"):
            sequence = self.env["ir.sequence"].create(
                {
                    "name": _("Sequence") + " " + vals["sequence_code"],
                    "padding": 5,
                    "prefix": vals["sequence_code"],
                    "company_id": vals.get("company_id"),
                }
            )
            vals["sequence_id"] = sequence.id

        request_category = super().create(vals)
        return request_category

    def write(self, vals):
        if "sequence_code" in vals:
            for request_category in self:
                sequence_vals = {
                    "name": _("Sequence") + " " + vals["sequence_code"],
                    "padding": 5,
                    "prefix": vals["sequence_code"],
                }
                if request_category.sequence_id:
                    request_category.sequence_id.write(sequence_vals)
                else:
                    sequence_vals["company_id"] = vals.get(
                        "company_id", request_category.company_id.id
                    )
                    sequence = self.env["ir.sequence"].create(sequence_vals)
                    request_category.sequence_id = sequence
        if "company_id" in vals:
            for request_category in self:
                if request_category.sequence_id:
                    request_category.sequence_id.company_id = vals.get("company_id")
        return super().write(vals)

    def create_request(self):
        self.ensure_one()
        res = {
            "type": "ir.actions.act_window",
            "res_model": "request.request",
            "views": [[False, "form"]],
            "context": {
                "form_view_initial_mode": "edit",
                "default_category_id": self.id,
            },
        }
        overwrite_vals = self._get_overwrite_vals()
        res["context"].update(overwrite_vals)
        return res

    def _get_overwrite_vals(self):
        """valid_dict = {
            "default_amount": 10000,
            "default_location": "G2 Building, Bangkok",
            "deafult_requested_by": env.user.id,
        }
        """
        self.ensure_one()
        overwrite_vals = self.context_overwrite or "{}"
        try:
            overwrite_vals = safe_eval(overwrite_vals, globals_dict={"env": self.env})
            assert isinstance(overwrite_vals, dict)
        except (SyntaxError, ValueError, AssertionError):
            raise ValidationError(_("Overwrite value must be a valid python dict"))
        return overwrite_vals


class RequestCategoryChildDocsOption(models.Model):
    _name = "request.category.child.doc.option"
    _description = "Child Documents Option"

    category_id = fields.Many2one(
        comodel_name="request.category",
        index=True,
        ondelete="cascade",
    )
    model = fields.Selection([], readonly=True, index=True)
    approved_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="After Approved Action",
        domain="[('usage', '=', 'ir_actions_server'),('model_id.model', '=', model)]",
        index=True,
        help="This server action is trigger after child document is approved",
    )
    rejected_action_id = fields.Many2one(
        comodel_name="ir.actions.server",
        string="After Rejected Action",
        domain="[('usage', '=', 'ir_actions_server'),('model_id.model', '=', model)]",
        index=True,
        help="This server action is trigger after child document is rejected",
    )
