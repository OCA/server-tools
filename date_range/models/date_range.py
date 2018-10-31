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
        comodel_name='date.range', string="Parent", index=1)

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
                text_dict = {
                    'name': this.name,
                    'start': this.date_start,
                    'end': this.date_end,
                    'parent_name': this.parent_id.name,
                    'parent_start': this.parent_id.date_start,
                    'parent_end': this.parent_id.date_end,
                }
                if (not start) and end:
                    text = _(
                        "Start date %(start)s of %(name)s must be greater than"
                        " or equal to "
                        "start date %(parent_start)s of %(parent_name)s"
                    ) % text_dict
                elif (not end) and start:
                    text = _(
                        "End date %(end)s of %(name)s must be smaller than"
                        " or equal to "
                        "end date %(parent_end)s of %(parent_name)s"
                    ) % text_dict
                else:
                    text = _(
                        "%(name)s range not in "
                        "%(parent_start)s - %(parent_end)s"
                    ) % text_dict
                raise ValidationError(
                    _("%(name)s not a subrange of"
                        " %(parent_name)s: " % text_dict) + text
                    )

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

    @api.multi
    @api.onchange('company_id', 'type_id', 'date_start', 'date_end')
    def onchange_type_id(self):
        """The type_id and the dates determine the choices for parent."""
        domain = []
        if self.company_id:
            domain.append(('company_id', '=', self.company_id.id))
        if self.parent_type_id:
            domain.append(('type_id', '=', self.parent_type_id.id))
        if self.date_start:
            domain.append('|')
            domain.append(('date_start', '<=', self.date_start))
            domain.append(('date_start', '=', False))
        if self.date_end:
            domain.append('|')
            domain.append(('date_end', '>=', self.date_end))
            domain.append(('date_end', '=', False))
        if domain:
            # If user did not select a parent already, autoselect the last
            # (ordered by date_start) or only parent that applies.
            if self.type_id and self.date_start and not self.parent_id:
                possible_parent = self.search(
                    domain, limit=1, order='date_start desc')
                self.parent_id = possible_parent  # can be empty!
        return {'domain': {'parent_id': domain}}
