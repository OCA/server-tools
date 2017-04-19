# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class InfrastructureConnector(models.Model):
    """Child modules should inherit this model to create new connector types.

    In the ``_get_interface_types`` method, new interfaces should add
    themselves::

        @api.model
        def _get_interface_types(self):
            res = super()._get_interface_types()
            return res + [('easypost', 'EasyPost')]

    The following methods must be implemented for each adapter, where
    ``<name>`` is equal to the interface name (``easypost`` in above):

        * ``<name>_get_client``: Return a usable API client for the
            validator.
        * ``<name>_test_connector``: Test the connection to the API, and
            escalate to super if success.
        * ``<name>_get_address``: Return the suggested address for a
            partner using the API. It should accept an authenticated API
            client as the first parameter and a ``res.partner`` singleton
            as the second.

    If the remote system does not disconnect automatically, destruction can
    be implemented in:

        * ``<name>_destroy_client``: Destroy the connection. It should accept
            an instance of the client as returned by ``<name>_get_client``.
    """

    _name = 'address.validate'
    _description = 'Address Validator Interface'
    _inherit = 'external.system.adapter'

    interface_type = fields.Selection(
        selection='_get_interface_types',
        required=True,
    )

    @api.model
    def _get_interface_types(self):
        """Child modules should add themselves to these selection values."""
        return []

    @api.multi
    def get_address(self, partner):
        """Returns an address suggestion from the interface.

        Args:
            partner (ResPartner): Partner record to get address for.

        Returns:
            dict: The suggested address. Should contain keys: ``street``,
                ``street2``, ``city``, ``state_id``, ``zip``, ``country_id``,
                ``is_valid``, and ``validation_messages``.
        """
        self.ensure_one()
        with self.interface.client() as client:
            return self.__interface_method('get_address')(client, partner)

    @api.multi
    def external_get_client(self):
        return self.__interface_method('get_client')()

    @api.multi
    def external_destroy_client(self, client):
        try:
            return self.__interface_method('destroy_client')(client)
        except AttributeError:
            pass

    @api.multi
    def external_test_connector(self):
        return self.__interface_method('test_connector')()

    def __interface_method(self, method_name):
        return getattr(self, '%s_%s' % (self.interface_type, method_name))
