from odoo import api, models, fields, _
from odoo.tools import safe_eval


class SecurityAudit(models.Model):
    _name = 'security.audit'
    _description = 'Security Audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    date = fields.Datetime(string='Last Check', reaonly=True)
    state = fields.Selection([('new', 'New'), ('success', 'Success'), ('fail', 'Fail')],
                             compute='_get_state')
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user, required=True)
    rule_ids = fields.One2many('security.audit.rule', 'audit_id', string='Rules')
    traceback = fields.Text('Taceback', compute='_get_traceback')

    @api.depends('rule_ids.state')
    def _get_state(self):
        for audit in self:
            if any(x.state == 'new' for x in audit.rule_ids):
                audit.state = 'new'
            elif any(x.state == 'fail' for x in audit.rule_ids):
                audit.state = 'fail'
            else:
                audit.state = 'success'

    @api.depends('rule_ids.traceback')
    def _get_traceback(self):
        for audit in self:
            audit.traceback = ''.join(audit.rule_ids.filtered('traceback').mapped('traceback'))

    @api.model
    def _process_check_audit(self):
        audits = self.search([])
        self.action_check_audit()
        audits.activity_unlink(['security_audit.mail_activity_audit_fail'])
        for audit in audits.filtered(lambda x: x.state == 'fail'):
            audit.activity_schedule('security_audit.mail_activity_audit_fail', user_id=audit.user_id.id)

    def action_check_audit(self):
        self.mapped('rule_ids').action_check_rule()
        self.write({'date': fields.Datetime.now()})
        for audit in self:
            audit.message_post(body=_('The result of the check is %s') % audit.state)


class SecurityRules(models.Model):
    _name = 'security.audit.rule'
    _description = 'Security Audit Rule'

    name = fields.Char(required=True)
    audit_id = fields.Many2one('security.audit', readonly=True, ondelete='cascade')
    model_id = fields.Many2one('ir.model', 'Object', required=True, ondelete='cascade')
    model_name = fields.Char(related='model_id.model')
    user_ids = fields.Many2many('res.users', string='Users')
    group_ids = fields.Many2many('res.groups', string='Groups')
    domain = fields.Char('Domain')
    check_read = fields.Boolean(string='Can\'t Read', default=True)
    check_write = fields.Boolean(string='Can\'t Write', default=True)
    check_create = fields.Boolean(string='Can\'t Create', default=True)
    check_unlink = fields.Boolean(string='Can\'t Delete', default=True)
    state = fields.Selection([('new', 'New'), ('success', 'Success'), ('fail', 'Fail')], reaonly=True)
    date = fields.Datetime(string='Last Check', readonly=True)
    traceback = fields.Text(string='Traceback', readonly=True)

    def action_check_rule(self):
        for rule in self:
            users = rule.user_ids | rule.group_ids.mapped('users')
            traceback = ''
            for user in users:

                for mode in ['read', 'write', 'unlink']:
                    if not rule['check_%s' % mode]:
                        continue

                    forbidden, total = rule._check_operation(mode, user)

                    if forbidden:
                        model = self.env[rule.model_id.model].sudo(user=user)
                        res = model.check_access_rights(mode, raise_exception=False)
                        if not res:
                            forbidden = 0

                    if forbidden:
                        traceback += '%s : %s can %s %s/%s %s (%s).\n' % (rule.name, user.name, mode, forbidden, total,
                                                                          rule.model_id.name, rule.model_id.model)

            if traceback:
                rule.state = 'fail'
                rule.traceback = traceback
            else:
                rule.state = 'success'
                rule.traceback = ''
            rule.date = fields.Datetime.now()

    def _check_operation(self, mode, user):
        self.ensure_one()
        Model = self.env[self.model_id.model].sudo(user=user).with_context(active_test=False)
        query = Model._where_calc(safe_eval(self.domain or '[]'))
        Model._apply_ir_rules(query, mode)
        from_clause, where_clause, where_clause_params = query.get_sql()

        where_str = where_clause and (' WHERE %s' % where_clause) or ''

        query_str = 'SELECT count(1) FROM ' + from_clause + where_str

        self._cr.execute(query_str, where_clause_params)
        res = self._cr.fetchone()

        self._cr.execute('SELECT count(1) FROM %s' % Model._table,)
        total = self._cr.fetchone()

        return res[0], total[0]
