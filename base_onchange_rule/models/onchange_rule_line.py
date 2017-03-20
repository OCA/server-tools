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
        comodel_name='ir.model.fields', string='Field',
        domain="[('model_id', '=', model_id)]", required=True,
        help="Select field that'll be driven by onchange "
             "according to implied record.")
    value = fields.Char(required=True)
    domain = fields.Char()
    readonly = fields.Boolean()

    @api.model
    def _authorised_models(self):
        if self.onchange_rule_id.implied_model:
            model = self.env['ir.model'].search(
                [('model', '=', self.onchange_rule_id.implied_model)])
            return [(model.model, model.name), ]
        else:
            return [('res.partner', 'Partner')]

    # @api.model
    # def default_get(self, fields):
    #     return {
    #         'implied_record': '%s,False' % self._authorised_models()[0][0]
    #     }

    @api.model
    def _check_line(self, vals):
        """ Check value and domain
        """
        # check value field
        value = vals.get('value') or self.value
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
        self._check_line(vals)
        return super(OnchangeRuleLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_line(vals)
        return super(OnchangeRuleLine, self).write(vals)

    # @api.model
    # def default_get(self, fields):
    #     active_id = self._context.get('active_id')
    #     origin = self.env['onchange.rule'].browse(active_id)
    #     if origin:
    #         return {
    #             'src_model_id': origin.model_id.id,
    #             'name': origin.name,
    #             'config_ids': self._deserialize_dict(origin)
    #         }
    #     return {}

    # def _deserialize_dict(self, setting):
    #     if not setting.config:
    #         return False
    #     valist = []
    #     for id, rule in ast.literal_eval(setting.config).items():
    #         implied_record = '%s,%s' % (setting.implied_model, id)
    #         for field, item in rule.items():
    #             values = {
    #                 'implied_record': implied_record,
    #                 'model_id': setting.model_id.id,
    #                 'field_id': self.env['ir.model.fields'].search([
    #                     ('name', '=', field),
    #                     ('relation', '=', setting.implied_model)]).id,
    #                 'value': str(item['value']),
    #             }

    #         valist.append((0, 0, values))
    #     print valist
    #     return valist

# [(0, 0, {'model_id': False, 'field_id': False, 'value': '1',
# 'implied_record': u'sale.covenant,1'})]

    # @api.model
    # def create(self, vals):

    # @api.multi
    # def write(self, vals):

    # def _default_implied_record(self, *args):
    #     return '%s,False' % self._implied_model

