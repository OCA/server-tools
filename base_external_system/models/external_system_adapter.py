# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ExternalSystemAdapter(models.AbstractModel):
    """This is the model that should be inherited for new external systems.

    Methods provided are prefixed with ``external_`` in order to keep from
    """

    _name = 'external.system.adapter'
    _description = 'External System Adapter'
    _inherits = {'external.system': 'system_id'}

    system_id = fields.Many2one(
        string='System',
        comodel_name='external.system',
        required=True,
        ondelete='cascade',
    )

    @api.multi
    @contextmanager
    def client(self):
        """Client object usable as a context manager to include destruction.

        Yields the result from ``external_get_client``, then calls
        ``external_destroy_client`` to cleanup the client.

        Yields:
            mixed: An object representing the client connection to the remote
             system.
        """
        self.ensure_one()
        client = self.external_get_client()
        try:
            yield client
        finally:
            self.external_destroy_client(client)

    @api.multi
    def external_get_client(self):
        """Return a usable client representing the remote system."""
        self.ensure_one()

    @api.multi
    def external_destroy_client(self, client):
        """Perform any logic necessary to destroy the client connection.

        Args:
            client (mixed): The client that was returned by
             ``external_get_client``.
        """
        self.ensure_one()

    @api.multi
    def external_test_connection(self):
        """Adapters should override this method, then call super if valid.

        If the connection is invalid, adapters should raise an instance of
        ``odoo.ValidationError``.

        Raises:
            odoo.exceptions.UserError: In the event of a good connection.
        """
        raise UserError(_('The connection was a success.'))
