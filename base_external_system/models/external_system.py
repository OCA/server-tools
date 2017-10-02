# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ExternalSystem(models.Model):

    _name = 'external.system'
    _description = 'External System'

    name = fields.Char(
        required=True,
        help='This is the canonical (humanized) name for the system.',
    )
    host = fields.Char(
        help='This is the domain or IP address that the system can be reached '
             'at.',
    )
    port = fields.Integer(
        help='This is the port number that the system is listening on.',
    )
    username = fields.Char(
        help='This is the username that is used for authenticating to this '
             'system, if applicable.',
    )
    password = fields.Char(
        help='This is the password that is used for authenticating to this '
             'system, if applicable.',
    )
    private_key = fields.Text(
        help='This is the private key that is used for authenticating to '
             'this system, if applicable.',
    )
    private_key_password = fields.Text(
        help='This is the password to unlock the private key that was '
             'provided for this sytem.',
    )
    fingerprint = fields.Text(
        help='This is the fingerprint that is advertised by this system in '
             'order to validate its identity.',
    )
    ignore_fingerprint = fields.Boolean(
        default=True,
        help='Set this to `True` in order to ignore an invalid/unknown '
             'fingerprint from the system.',
    )
    remote_path = fields.Char(
        help='Restrict to this directory path on the remote, if applicable.',
    )
    company_ids = fields.Many2many(
        string='Companies',
        comodel_name='res.company',
        required=True,
        default=lambda s: [(6, 0, s.env.user.company_id.ids)],
        help='Access to this system is restricted to these companies.',
    )
    system_type = fields.Selection(
        selection='_get_system_types',
        required=True,
    )
    interface = fields.Reference(
        selection='_get_system_types',
        readonly=True,
        help='This is the interface that this system represents. It is '
             'created automatically upon creation of the external system.',
    )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Connection name must be unique.'),
    ]

    @api.model
    def _get_system_types(self):
        """Return the adapter interface models that are installed."""
        adapter = self.env['external.system.adapter']
        return [
            (m, self.env[m]._description) for m in adapter._inherit_children
        ]

    @api.multi
    @api.constrains('fingerprint', 'ignore_fingerprint')
    def check_fingerprint_ignore_fingerprint(self):
        """Do not allow a blank fingerprint if not set to ignore."""
        for record in self:
            if not record.ignore_fingerprint and not record.fingerprint:
                raise ValidationError(_(
                    'Fingerprint cannot be empty when Ignore Fingerprint is '
                    'not checked.',
                ))

    @api.model
    def create(self, vals):
        """Create the interface for the record and assign to ``interface``."""
        record = super(ExternalSystem, self).create(vals)
        interface = self.env[vals['system_type']].create({
            'system_id': record.id,
        })
        record.interface = interface
        return record

    @api.multi
    @contextmanager
    def client(self):
        """Client object usable as a context manager to include destruction.

        Yields the result from ``interface.external_get_client``, then calls
        ``interface.external_destroy_client`` to cleanup the client.

        Yields:
            mixed: An object representing the client connection to the remote
             system.
        """
        self.ensure_one()
        client = self.interface.external_get_client()
        try:
            yield client
        finally:
            self.interface.external_destroy_client(client)

    @api.multi
    def action_test_connection(self):
        """Test the connection to the external system."""
        self.ensure_one()
        self.interface.external_test_connection()
