from odoo import api, fields, models


class OnchangeHelperTestModel(models.Model):
    _name = 'onchange.helper.test.model'
    _description = 'onchange.helper.test.model'

    name = fields.Char()
    output = fields.Char()
    line_ids = fields.One2many('onchange.helper.test.model.line', 'super_id')

    @api.onchange('name', 'line_ids')
    def _onchange_name(self):
        # we need to be able to access fields on _origin here
        self.output = self.name + ': ' + ', '.join(
            self._origin.mapped('line_ids.name')
        )


class OnchangeHelperTestModelLine(models.Model):
    _name = 'onchange.helper.test.model.line'
    _description = 'onchange.helper.test.model.line'

    name = fields.Char()
    super_id = fields.Many2one('onchange.helper.test.model')
