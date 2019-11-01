# Copyright (C) 2019 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models, SUPERUSER_ID


class IrModelFieldsRecompute(models.Model):
    _name = 'ir.model.fields.recompute'
    _description = 'Fields Recomputes'

    _STATE_SELECTION = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('done', 'Done'),
    ]

    name = fields.Char(required=True)

    model_id = fields.Many2one(
        string='Model', comodel_name='ir.model', required=True, readonly=True,
        states={'draft': [('readonly', False)]})

    compute_function = fields.Char(
        string='Compute Function', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    field_ids = fields.Many2many(
        compute="_compute_field_ids", comodel_name="ir.model.fields")

    limit = fields.Integer(default=1000)

    domain = fields.Char(default="[]")

    order = fields.Char(default="id desc")

    state = fields.Selection(
        selection=_STATE_SELECTION, required=True, default='draft')

    current_qty = fields.Integer(string="Currenty Quantity", readonly=True)

    total_qty = fields.Integer(string="Total Quantity", readonly=True)

    progress = fields.Float(
        string="Progress", compute='_compute_progress',
        store=True, help="Display progress of current recomputation.")

    check_field_id = fields.Many2one(
        string="Odoo Check Field", comodel_name='ir.model.fields',
        readonly=True, help="Extra Boolean Field created on the target model"
        " that indicates which items has been recomputed.")

    cron_id = fields.Many2one(
        string='Odoo Cron', comodel_name='ir.cron', readonly=True,
        help="Cron Task that will refresh the materialized view")

    @api.multi
    def _get_field_ids(self):
        self.ensure_one()

    @api.depends('model_id', 'compute_function')
    def _compute_field_ids(self):
        IrModelFields = self.env['ir.model.fields']
        for recompute in self:
            CurrentModel = self.env[recompute.model_id.model]
            if not recompute.model_id or not recompute.compute_function:
                continue
            field_names = []
            for name, orm_field in CurrentModel._fields.items():
                if orm_field.compute == recompute.compute_function:
                    field_names.append(name)
            recompute.field_ids = IrModelFields.search([
                ('name', 'in', field_names),
                ('model', '=', recompute.model_id.model),
            ]).ids

    @api.depends('current_qty', 'total_qty')
    def _compute_progress(self):
        for recompute in self:
            if recompute.total_qty == 0:
                recompute.progress = 100
            else:
                recompute.progress = round(
                    100.0 * recompute.current_qty / recompute.total_qty, 2)

    def button_enable(self):
        IrModelFields = self.env['ir.model.fields']
        IrCron = self.env['ir.cron']
        recomputes = self.filtered(lambda x: x.state == 'draft')
        for recompute in recomputes:
            # create field
            recompute.check_field_id = IrModelFields.create(
                self._prepare_check_field())
            recompute.cron_id = IrCron.create(self._prepare_cron())
            self.env.cr.execute("UPDATE {table} SET {column} = False;".format(
                table=self.env[recompute.model_id.model]._table,
                column=recompute.check_field_id.name))
            recompute.state = 'pending'
            recompute._update_progression()

    def button_draft(self):
        recomputes = self.filtered(lambda x: x.state != 'draft')
        if recomputes.mapped('check_field_id'):
            recomputes.mapped('check_field_id').unlink()
        if recomputes.mapped('cron_id'):
            recomputes.mapped('check_field_id').unlink()
        recomputes.write({'state': 'draft'})

    def button_run(self):
        self.ensure_one()
        self.cron_id.method_direct_trigger()

    # Overload Section
    def unlink(self):
        self.button_draft()
        super().unlink()

    # Private Function
    def _prepare_check_field(self):
        self.ensure_one()
        return {
            'model_id': self.model_id.id,
            'model': self.model_id.model,
            'name': 'x_recompute_field_%d' % self.id,
            'field_description': "Recompute '%s' Done" % self.compute_function,
            'ttype': 'boolean',
            'interval_type': 'hours',
            'active': True,
        }

    def _prepare_cron(self):
        self.ensure_one()
        return {
            'name': _("Run {model}.{function}()".format(
                model=self.model_id.model, function=self.compute_function
            )),
            'user_id': SUPERUSER_ID,
            'model_id': self.env['ir.model'].search([
                ('model', '=', self._name)], limit=1).id,
            'state': 'code',
            'code': 'model._run_cron(%s)' % self.ids,
            'numbercall': -1,
        }

    @api.model
    def _run_cron(self, recompute_ids):
        recomputes = self.browse(recompute_ids)
        for recompute in recomputes:
            recompute._run()

    @api.multi
    def _run(self):
        self.ensure_one()
        if len(self.field_ids) == 0:
            return
        CurrentModel = self.env[self.model_id.model]
        domain = [(self.check_field_id.name, '=', -False)] + eval(self.domain)
        objects = CurrentModel.search(
            domain, order=self.order, limit=self.limit)
        getattr(objects, self.compute_function)()
        objects.write({self.check_field_id.name: True})
        self._update_progression()

    def _update_progression(self):
        for recompute in self.filtered(lambda x: x.state != 'draft'):
            CurrentModel = self.env[recompute.model_id.model]
            domain = [(self.check_field_id.name, '=', -True)]
            recompute.current_qty = CurrentModel.search(domain, count=True)
            domain = eval(recompute.domain)
            recompute.total_qty = CurrentModel.search(domain, count=True)
            if recompute.current_qty == recompute.total_qty:
                recompute.state = 'done'
                recompute.cron_id.active = False
