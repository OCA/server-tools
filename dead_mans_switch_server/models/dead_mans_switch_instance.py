# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
from datetime import datetime, timedelta
from openerp import _, api, fields, models


class DeadMansSwitchInstance(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'dead.mans.switch.instance'
    _description = 'Instance to monitor'
    _order = 'state, partner_id'
    _rec_name = 'partner_id'

    state = fields.Selection(
        [('new', 'New'), ('active', 'Active'), ('suspended', 'Suspended')],
        'State', default='new')
    partner_id = fields.Many2one(
        'res.partner', 'Customer',
        domain=[('is_company', '=', True), ('customer', '=', True)])
    database_uuid = fields.Char('Database id', required=True, readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible user',
                              track_visibility='onchange')
    description = fields.Char('Description')
    log_ids = fields.One2many(
        'dead.mans.switch.log', 'instance_id', string='Log lines')
    alive = fields.Boolean(
        'Alive', compute='_compute_alive', search='_search_alive')
    alive_max_delay = fields.Integer(
        'Alive delay', help='The amount of seconds without notice after which '
        'the instance is considered dead', default=600)
    last_seen = fields.Datetime('Last seen', compute='_compute_last_log')
    last_cpu = fields.Float('CPU', compute='_compute_last_log')
    last_cpu_sparkline = fields.Text('CPU', compute='_compute_last_log')
    last_ram = fields.Float('RAM', compute='_compute_last_log')
    last_ram_sparkline = fields.Text('RAM', compute='_compute_last_log')
    last_user_count = fields.Integer(
        'Active users', compute='_compute_last_log')
    last_user_count_sparkline = fields.Text(
        'Active users', compute='_compute_last_log')

    _sql_constraints = [
        ('uuid_unique', 'unique(database_uuid)', 'Database ID must be unique'),
    ]

    @api.multi
    def name_get(self):
        return [
            (
                this.id,
                '%s%s' % (
                    this.partner_id.name or this.database_uuid,
                    ' (%s)' % (this.description) if this.description else '',
                )
            )
            for this in self
        ]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if not self.user_id:
            self.user_id = self.partner_id.user_id

    @api.multi
    def button_active(self):
        self.write({'state': 'active'})

    @api.multi
    def button_suspended(self):
        self.write({'state': 'suspended'})

    @api.multi
    def button_logs(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dead.mans.switch.log',
            'domain': [('instance_id', 'in', self.ids)],
            'name': _('Logs'),
            'view_mode': 'graph,tree,form',
            'context': {
                'search_default_this_month': 1,
            },
        }

    @api.multi
    def _compute_alive(self):
        for this in self:
            if this.state in ['new', 'suspended']:
                this.alive = False
                continue
            this.alive = bool(
                self.env['dead.mans.switch.log'].search(
                    [
                        ('instance_id', '=', this.id),
                        ('create_date', '>=', fields.Datetime.to_string(
                            datetime.utcnow() -
                            timedelta(seconds=this.alive_max_delay))),
                    ],
                    limit=1))

    @api.model
    def _search_alive(self, operator, value):
        alive = True if operator == '=' and value or\
            operator == '!=' and not value else False
        self.env.cr.execute(
            'select i.id from dead_mans_switch_instance i '
            'left join (select instance_id, max(create_date) create_date '
            'from dead_mans_switch_log group by instance_id) l '
            'on l.instance_id=i.id '
            "where coalesce(l.create_date, '1970-01-01'::timestamp) %s "
            "now() at time zone 'utc' - "
            "(2 * alive_max_delay || 'seconds')::interval "
            "group by i.id " %
            (alive and '>=' or '<'))
        return [('id', 'in', [i for i, in self.env.cr.fetchall()])]

    @api.multi
    def _compute_last_log(self):
        for this in self:
            last_log = self.env['dead.mans.switch.log'].search(
                [('instance_id', '=', this.id)], limit=12)
            field_mapping = {
                'last_seen': 'create_date',
                'last_cpu': 'cpu',
                'last_ram': 'ram',
                'last_user_count': 'user_count',
            }
            for field, mapped_field in field_mapping.iteritems():
                this[field] = last_log[:1][mapped_field]
            sparkline_fields = ['last_cpu', 'last_ram', 'last_user_count']
            for field in sparkline_fields:
                this['%s_sparkline' % field] = json.dumps(
                    list(reversed(last_log.mapped(lambda log: {
                        'value': log[field_mapping[field]],
                        'tooltip': log.create_date,
                    }))))

    @api.model
    def check_alive(self):
        """handle cronjob"""
        for this in self.search(self._needaction_domain_get()):
            this.panic()

    @api.multi
    def panic(self):
        """override for custom handling"""
        self.ensure_one()
        last_post = fields.Datetime.from_string(self.message_last_post)
        if last_post and last_post >= datetime.utcnow() - 3 * timedelta(
                seconds=self.alive_max_delay):
            # don't nag too often
            return
        self.message_post(
            type='comment', subtype='mt_comment',
            subject=_('Dead man\'s switch warning: %s') %
            self.display_name, content_subtype='plaintext',
            body=_('%s seems to be dead') % self.display_name)

    @api.model
    def _needaction_domain_get(self):
        return [('alive', '=', False), ('state', '=', 'active')]
