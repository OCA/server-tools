# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, exceptions, fields, models


class VacuumRule(models.Model):
    _name = "vacuum.rule"
    _description = "Rules Used to delete message historic"

    @api.depends('model_ids')
    @api.multi
    def _get_model_id(self):
        for rule in self:
            if rule.model_ids and len(rule.model_ids) == 1:
                rule.model_id = rule.model_ids.id
                rule.model = rule.model_id.model
            else:
                rule.model_id = False
                rule.model = False

    name = fields.Char(required=True)
    ttype = fields.Selection(
        selection=[('attachment', 'Attachment'),
                   ('message', 'Message')],
        string="Type",
        required=True)
    filename_pattern = fields.Char(
        help=("If set, only attachments containing this pattern will be"
              " deleted."))
    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env['res.company']._company_default_get(
            'vacuum.rule'))
    message_subtype_ids = fields.Many2many(
        'mail.message.subtype', string="Subtypes",
        help="Message subtypes concerned by the rule. If left empty, the "
             "system won't take the subtype into account to find the "
             "messages to delete")
    empty_subtype = fields.Boolean(
        help="Take also into account messages with no subtypes")
    model_ids = fields.Many2many(
        'ir.model', string="Models",
        help="Models concerned by the rule. If left empty, it will take all "
             "models into account")
    model_id = fields.Many2one(
        'ir.model', readonly=True,
        compute='_get_model_id',
        help="Technical field used to set attributes (invisible/required, "
             "domain, etc...for other fields, like the domain filter")
    model_filter_domain = fields.Text(
        string='Model Filter Domain')
    model = fields.Char(
        readonly=True,
        compute='_get_model_id',
        string='Model code'
    )
    message_type = fields.Selection([
        ('email', 'Email'),
        ('comment', 'Comment'),
        ('notification', 'System notification'),
        ('all', 'All')])
    retention_time = fields.Integer(
        required=True, default=365,
        help="Number of days the messages concerned by this rule will be "
             "keeped in the database after creation. Once the delay is "
             "passed, they will be automatically deleted.")
    active = fields.Boolean(default=True)
    description = fields.Text()

    @api.multi
    @api.constrains('retention_time')
    def retention_time_not_null(self):
        for rule in self:
            if not rule.retention_time:
                raise exceptions.ValidationError(
                    _("The Retention Time can't be 0 days"))

    def _search_autovacuum_records(self):
        self.ensure_one()
        model = self.ttype
        if model == 'message':
            model = 'mail.message'
        elif model == 'attachment':
            model = 'ir.attachment'
        return self.env[model]._get_autovacuum_records(self)
