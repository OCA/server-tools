# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from odoo.exceptions import UserError


class OnchangeRuleLine(models.TransientModel):
    _name = 'onchange.rule.line'
    _description = "Onchange Rule Lines"

    onchange_rule_id = fields.Many2one(
        comodel_name='onchange.rule', string="Onchange Rules", required=True)
    implied_record = fields.Reference(
        selection='_authorised_models', string="Implied Record", required=True,
        help="Select the object that'll execute onchange.")
    sequence = fields.Integer(string='Sequence')
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True)
    field_id = fields.Many2one(
        comodel_name='ir.model.fields', string='Destination Field',
        domain="[('model_id', '=', model_id), "
               "('ttype', 'in', ('many2one', 'selection'))]",
        required=True,
        help="Select field that'll be driven by onchange "
             "according to implied record.")
    selection_value = fields.Char()
    m2o_value = fields.Reference(
        selection='_authorised_models', string="Many2one Value",
        help="Final value after onchange is executed")
    readonly = fields.Boolean()
    domain = fields.Char()

    @api.model
    def _authorised_models(self):
        return [(x.model, x.name) for x in self.env['ir.model'].search([])]

    @api.multi
    @api.onchange('field_id')
    def _compute_m2o_value(self):
        for rec in self:
            if rec.field_id.relation:
                last = self.env[rec.field_id.relation].search(
                    [], order='id desc', limit=1)
                rec.m2o_value = '%s,%s' % (rec.field_id.relation, last.id)

    @api.model
    def default_get(self, fields):
        implied_record = False
        if self._context.get('implied_model'):
            last = self.env[self._context['implied_model']].search(
                [], order='id desc', limit=1)
            implied_record = '%s,%s' % (
                self._context['implied_model'], last.id)
        return {
            'implied_record': implied_record,
            'model_id': self._context.get('default_model_id')
        }

    @api.model
    def _check_line(self, vals):
        """ Check value and domain
        """
        # TODO transformer pour champ selection
        value = vals.get('selection_value') or self.selection_value
        field_id = vals.get('field_id') or self.field_id.id
        field = self.env['ir.model.fields'].browse(field_id)
        origin_obj = self.env[field.relation].search([('id', '=', int(value))])
        if not origin_obj:
            raise UserError(
                "'%s' value doesn't exist in model '%s'. "
                "Choose an existing value" % (
                    value, origin_obj._description))
        # TODO check domain
        return True

    @api.model
    def create(self, vals):
        # self._check_line(vals)
        return super(OnchangeRuleLine, self).create(vals)

    @api.multi
    def write(self, vals):
        # self._check_line(vals)
        return super(OnchangeRuleLine, self).write(vals)
