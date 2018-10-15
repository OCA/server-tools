# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DateRangeType(models.Model):
    _name = "date.range.type"
    _description = "Date Range Type"

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    name = fields.Char(required=True, translate=True)
    allow_overlap = fields.Boolean(
        help="If sets date range of same type must not overlap.",
        default=False)
    active = fields.Boolean(
        help="The active field allows you to hide the date range without "
        "removing it.", default=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', index=1,
        default=_default_company)
    date_range_ids = fields.One2many('date.range', 'type_id', string='Ranges')
    parent_type_id = fields.Many2one(
        comodel_name='date.range.type',
        index=1)

    _sql_constraints = [
        ('date_range_type_uniq', 'unique (name,company_id)',
         'A date range type must be unique per company !')]

    @api.constrains('company_id')
    def _check_company_id(self):
        if not self.env.context.get('bypass_company_validation', False):
            for rec in self.sudo():
                if not rec.company_id:
                    continue
                if bool(rec.date_range_ids.filtered(
                        lambda r: r.company_id and
                        r.company_id != rec.company_id)):
                    raise ValidationError(
                        _('You cannot change the company, as this '
                          'Date Range Type is  assigned to Date Range '
                          '(%s).') % (rec.date_range_ids.name_get()[0][1]))

    @api.constrains('parent_type_id')
    def _validate_parent_type_id(self):
        for record in self:
            parent = record
            while parent:
                if not parent.parent_type_id:
                    break
                if record.parent_type_id == parent:
                    raise ValidationError(
                        _("A type parent  can not have a parent:"
                          " %s can not have %s as parent") % (
                            parent.name, record.name))
                parent = parent.parent_type_id
