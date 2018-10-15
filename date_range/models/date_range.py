# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DateRange(models.Model):
    _name = "date.range"
    _order = "type_name,date_start"

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    name = fields.Char(required=True, translate=True)
    date_start = fields.Date(string='Start date', required=True)
    date_end = fields.Date(string='End date', required=True)
    type_id = fields.Many2one(
        comodel_name='date.range.type', string='Type', index=1, required=True)
    type_name = fields.Char(
        string='Type', related='type_id.name', readonly=True, store=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', index=1,
        default=_default_company)
    active = fields.Boolean(
        help="The active field allows you to hide the date range without "
        "removing it.", default=True)
    parent_type_id = fields.Many2one(
        related='type_id.parent_type_id',
        store=True,
        readonly=True)
    parent_id = fields.Many2one(
        comodel_name='date.range', string="Parent",
        domain="['|', ('type_id.parent_type_id', '!=', parent_type_id), "
        "('parent_type_id', '=', False)]",
        index=1)

    _sql_constraints = [
        ('date_range_uniq', 'unique (name,type_id, company_id)',
         'A date range must be unique per company !')]

    @api.constrains('parent_id', 'date_start', 'date_end')
    def _validate_child_range(self):
        for this in self:
            if not this.parent_id:
                continue
            start = this.parent_id.date_start <= this.date_start
            end = this.parent_id.date_end >= this.date_end
            child_range = start and end
            if not child_range:
                if (not start) and end:
                    text = _("Start dates are not compatible (%s < %s)") % (
                        this.date_start, this.parent_id.date_start)
                elif (not end) and start:
                    text = _("End dates are not compatible (%s > %s)") % (
                        this.date_end, this.parent_id.date_end)
                else:
                    text = _("%s range not in %s - %s") % (
                        this.name,
                        this.parent_id.date_start,
                        this.parent_id.date_end,
                    )
                raise ValidationError(
                    _("%s not a subrange of %s: " + text) % (
                        this.name, this.parent_id.name))

    @api.constrains('type_id', 'date_start', 'date_end', 'company_id')
    def _validate_range(self):
        for this in self:
            start = fields.Date.from_string(this.date_start)
            end = fields.Date.from_string(this.date_end)
            if start > end:
                raise ValidationError(
                    _("%s is not a valid range (%s > %s)") % (
                        this.name, this.date_start, this.date_end))
            if this.type_id.allow_overlap:
                continue
            # here we use a plain SQL query to benefit of the daterange
            # function available in PostgresSQL
            # (http://www.postgresql.org/docs/current/static/rangetypes.html)
            SQL = """
                SELECT
                    id
                FROM
                    date_range dt
                WHERE
                    DATERANGE(dt.date_start, dt.date_end, '[]') &&
                        DATERANGE(%s::date, %s::date, '[]')
                    AND dt.id != %s
                    AND dt.active
                    AND dt.company_id = %s
                    AND dt.type_id=%s;"""
            self.env.cr.execute(SQL, (this.date_start,
                                      this.date_end,
                                      this.id,
                                      this.company_id.id or None,
                                      this.type_id.id))
            res = self.env.cr.fetchall()
            if res:
                dt = self.browse(res[0][0])
                raise ValidationError(
                    _("%s overlaps %s") % (this.name, dt.name))

    @api.multi
    def get_domain(self, field_name):
        self.ensure_one()
        return [(field_name, '>=', self.date_start),
                (field_name, '<=', self.date_end)]
