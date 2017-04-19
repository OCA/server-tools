# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardAddressValidate(models.TransientModel):
    _name = 'wizard.address.validate'
    _description = 'Validate Address Wizard'

    partner_id = fields.Many2one(
        string='Partner',
        comodel_name='res.partner',
        required=True,
        default=lambda s: s._default_partner_id(),
    )
    interface_id = fields.Many2one(
        string='Validation Interface',
        comodel_name='address.validate',
        default=lambda s: s._default_interface_id(),
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    zip = fields.Char()
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state',
    )
    country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
    )
    latitude = fields.Float()
    longitude = fields.Float()
    is_valid = fields.Boolean()
    validation_messages = fields.Text()
    street_original = fields.Char(
        related='partner_id.street',
        readonly=True,
    )
    street2_original = fields.Char(
        related='partner_id.street2',
        readonly=True,
    )
    city_original = fields.Char(
        related='partner_id.city',
        readonly=True,
    )
    zip_original = fields.Char(
        related='partner_id.zip',
        readonly=True,
    )
    state_id_original = fields.Many2one(
        string='State',
        comodel_name='res.country.state',
        related='partner_id.state_id',
        readonly=True,
    )
    country_id_original = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        related='partner_id.country_id',
        readonly=True,
    )
    latitude_original = fields.Float(
        string='Latitude',
        related='partner_id.latitude',
    )
    longitude_original = fields.Float(
        string='Longitude',
        related='partner_id.longitude',
    )

    @api.model
    def _default_partner_id(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'res.partner':
            return active_id
        if active_model == 'res.company':
            company = self.env['res.company'].browse(active_id)
            return company.partner_id.id

    @api.model
    def _default_interface_id(self):
        return self.env.user.company_id.default_address_validate_id.id

    @api.multi
    def action_validate(self):
        """Get the suggested address from the provider."""
        self.ensure_one()
        self.write(
            self.interface_id.get_address(self.partner_id)
        )
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'src_model': 'res.partner',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def action_confirm(self):
        """Copy the validated information to the partner."""
        for record in self:
            record.partner_id.write({
                'street': record.street,
                'street2': record.street2,
                'city': record.city,
                'state_id': record.state_id.id,
                'country_id': record.country_id.id,
                'zip': record.zip,
            })
        return {
            'type': 'ir.actions.act_window_close',
        }
