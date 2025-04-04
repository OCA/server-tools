# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import socket

from odoo import api, fields, models


class ResRemote(models.Model):
    _name = "res.remote"
    _description = "Remotes"

    name = fields.Char(required=True, string="Hostname", index=True, readonly=True)
    ip = fields.Char(required=True)
    in_network = fields.Boolean(
        required=True, help="Shows if the remote can be found through the socket"
    )

    _sql_constraints = [("name_unique", "unique(name)", "Hostname must be unique")]

    @api.model
    def _create_vals(self, addr, hostname):
        return {
            "name": hostname or addr,
            "ip": addr,
            "in_network": bool(hostname),
        }

    @api.model
    def _get_remote(self, addr):
        try:
            hostname, alias, ips = socket.gethostbyaddr(addr)
        except socket.herror:
            logging.warning(f"Remote with ip {addr} could not be found")
            hostname = False
        remote = self.search([("name", "=ilike", hostname or addr)])
        if not remote:
            remote = self.create(self._create_vals(addr, hostname))
        if remote.ip != addr:
            # IPs can change through time, but hostname should not change
            remote.write({"ip": addr})
        return remote
