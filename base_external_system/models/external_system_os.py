# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from contextlib import contextmanager

from odoo import api, models


class ExternalSystemOs(models.AbstractModel):
    """This is an Interface implementing the OS module.

    For the most part, this is just a sample of how to implement an external
    system interface. This is still a fully usable implementation, however.
    """

    _name = 'external.system.os'
    _inherit = 'external.system.adapter'
    _description = 'External System OS'

    previous_dir = None

    @api.multi
    def external_get_client(self):
        """Return a usable client representing the remote system."""
        super(ExternalSystemOs, self).external_get_client()
        if self.system_id.remote_path:
            self.previous_dir = os.getcwd()
            os.chdir(self.system_id.remote_path)
        return os

    @api.multi
    def external_destroy_client(self, client):
        """Perform any logic necessary to destroy the client connection.

        Args:
            client (mixed): The client that was returned by
             ``external_get_client``.
        """
        super(ExternalSystemOs, self).external_destroy_client(client)
        if self.previous_dir:
            os.chdir(self.previous_dir)
            self.previous_dir = None
