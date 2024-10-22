# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from odoo import api, models


class ExternalSystemAdapterOs(models.AbstractModel):
    """This is an Interface implementing the OS module.

    For the most part, this is just a sample of how to implement an external
    system interface. This is still a fully usable implementation, however.
    """

    _name = "external.system.adapter.os"
    _inherit = "external.system.adapter"
    _description = "External System OS"

    def get_previous_dir(self):
        """Get previous_dir from adapter_memory."""
        return self.env.context["adapter_memory"].get("previous_dir", None)

    def set_previous_dir(self, value):
        """Store previous_dir in adapter_memor."""
        self.env.context["adapter_memory"]["previous_dir"] = value

    def del_previous_dir(self):
        """Get system from environment."""
        if "previous_dir" in self.env.context["adapter_memory"]:
            del self.env.context["adapter_memory"]["previous_dir"]

    previous_dir = property(get_previous_dir, set_previous_dir, del_previous_dir)

    @api.model
    def external_get_client(self):
        """Return a usable client representing the remote system."""
        if self.system_id.remote_path:
            self.previous_dir = os.getcwd()
            os.chdir(self.system_id.remote_path)
        return os

    @api.model
    def external_destroy_client(self, client):
        """Perform any logic necessary to destroy the client connection.

        Args:
            client (mixed): The client that was returned by
             ``external_get_client``.
        """
        if self.previous_dir:
            os.chdir(self.previous_dir)
            self.previous_dir = None
