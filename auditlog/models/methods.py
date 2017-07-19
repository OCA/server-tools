# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class AuditlogMethods(models.Model):
    _name = 'auditlog.methods'
    _description = 'Auditlog custom methods'
    _order = 'name'

    name = fields.Char(required=True)
    message = fields.Char(required=True)
    rule_id = fields.Many2one('auditlog.rule', readonly=True)
    use_active_ids = fields.Boolean(default=False)
    context_field_number = fields.Integer(default=0)
