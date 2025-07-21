from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    vapi_api_key = fields.Char('User Vapi API Key', copy=False, index=True)

    _sql_constraints = [
        ('vapi_api_key_unique', 'unique(vapi_api_key)', 'User Vapi API Key tiene que ser unico de cada usuario.'),
    ]

    @api.constrains('vapi_api_key')
    def _check_vapi_api_key(self):
        for user in self:
            if user.vapi_api_key:
                # Chequeo adicional por si el constraint de SQL no se activa por algún motivo
                users = self.search([
                    ('vapi_api_key', '=', user.vapi_api_key),
                    ('id', '!=', user.id)
                ])
                if users:
                    raise ValidationError('User Vapi API Key tiene que ser unico de cada usuario.')