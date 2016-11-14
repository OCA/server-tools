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

    _sql_constraints = [
        ('date_range_uniq', 'unique (name,type_id, company_id)',
         'A date range must be unique per company !')]

    @api.constrains('type_id', 'date_start', 'date_end', 'company_id')
    def _validate_range(self):
        for this in self:
            start = fields.Date.from_string(this.date_start)
            end = fields.Date.from_string(this.date_end)
            if start >= end:
                raise ValidationError(
                    _("%s is not a valid range (%s >= %s)") % (
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
