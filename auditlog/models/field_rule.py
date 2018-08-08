# © 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields
from .rule import FIELDS_BLACKLIST


class AuditlogFieldRule(models.Model):
    _name = 'auditlog.field.rule'
    _description = "Auditlog - Field rule"

    _rec_name = 'field_id'
    rule_id = fields.Many2one(
        'auditlog.rule', "Audit Rule", required=True, ondelete="cascade")
    model_id = fields.Many2one(
        'ir.model', "Model", related="rule_id.model_id", readonly=True)
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field",
        domain="[('model_id','=',model_id),('name','not in'," + str(
            FIELDS_BLACKLIST) + ")]",
        required=True,
    )

    user_ids = fields.Many2many(
        'res.users',
        'audittail_field_rules_users',
        'user_id', 'field_rule_id',
        string="Users",
        help="if  User is not added then it will applicable for all users")
    log_read = fields.Boolean(
        "Log Reads",
        help=("Select this if you want to keep track of read/open on any "
              "record of the field of this rule"))
    log_write = fields.Boolean(
        "Log Writes", default=True,
        help=("Select this if you want to keep track of modification on any "
              "record of the field of this rule"))
    log_unlink = fields.Boolean(
        "Log Deletes", default=True,
        help=("Select this if you want to keep track of deletion on any "
              "record of the field of this rule"))
    log_create = fields.Boolean(
        "Log Creates", default=True,
        help=("Select this if you want to keep track of creation on any "
              "record of the field of this rule"))
