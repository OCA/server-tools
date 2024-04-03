# Copyright 2017 LasLabs Inc.
# Copyright 2023 Therp BV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
"""Define the interface for external system adapters."""


from odoo import _, api, models
from odoo.exceptions import UserError


class ExternalSystemAdapter(models.AbstractModel):
    """This is the model that should be inherited for new external systems.

    Methods provided are prefixed with ``external_`` in order to keep from
    """

    _name = "external.system.adapter"
    _description = "External System Adapter"

    def get_system(self):
        """Get system from environment."""
        return self.env.context.get("system", None)

    system_id = property(get_system)

    @api.model
    def external_get_client(self):
        """Return a usable client representing the remote system."""
        self._raise_not_implemented()

    @api.model
    def external_destroy_client(self, client):
        """Perform any logic necessary to destroy the client connection.

        Args:
            client (mixed): The client that was returned by
             ``external_get_client``.
        """
        self._raise_not_implemented()

    def _raise_not_implemented(self):
        """Raise errors for methods that should be implemented in subclass."""
        raise UserError(_("Method not implemented in base adapter class."))
