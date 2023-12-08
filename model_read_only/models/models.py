# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.tools.safe_eval import safe_eval


class ModelReadonlyRestriction(models.Model):
    _name = "model.readonly.restriction"
    _description = "Model Readonly Restriction"

    model_id = fields.Many2one("ir.model")
    model_name = fields.Char(related="model_id.model")
    restriction_domain = fields.Char(
        "Domain", help="If empty - restriction is applied always."
    )
    group_ids = fields.Many2many(
        "res.groups",
        relation="res_group_model_readonly_restriction_rel",
        string="Groups",
        help="If empty - restriction is applied for everyone.",
    )


class IrModel(models.Model):
    _inherit = "ir.model"

    readonly_restriction_ids = fields.One2many("model.readonly.restriction", "model_id")


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        if operation != "read":
            model = self.env["ir.model"]._get(self._name)
            no_access = False
            for restr in model.sudo().readonly_restriction_ids:
                if restr.restriction_domain and self:
                    filtered_rec_id = self.filtered_domain(
                        safe_eval(restr.restriction_domain)
                    )
                    if filtered_rec_id and restr.group_ids & self.env.user.groups_id:
                        no_access = True
                elif (
                    not restr.restriction_domain
                    and restr.group_ids & self.env.user.groups_id
                ):
                    no_access = True
                if no_access and raise_exception:
                    raise exceptions.AccessError(
                        _("You are not allowed to modify this record.")
                    )
                elif no_access:
                    return False
        return super(BaseModel, self).check_access_rights(operation, raise_exception)
