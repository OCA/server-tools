# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# Copyright 2023 Therp BV.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from contextlib import contextmanager

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ExternalSystem(models.Model):

    _name = "external.system"
    _description = "External System"

    name = fields.Char(
        required=True, help="This is the canonical (humanized) name for the system."
    )
    scheme = fields.Char(
        help="This is the protocol used to communicate with the system."
    )
    host = fields.Char(
        help="This is the domain or IP address that the system can be reached at."
    )
    port = fields.Integer(
        help="This is the port number that the system is listening on."
    )
    username = fields.Char(
        help="This is the username that is used for authenticating to this"
        " system, if applicable."
    )
    password = fields.Char(
        help="This is the password that is used for authenticating to this"
        " system, if applicable."
    )
    private_key = fields.Text(
        help="This is the private key that is used for authenticating to"
        " this system, if applicable."
    )
    private_key_password = fields.Text(
        help="This is the password to unlock the private key that was"
        " provided for this sytem."
    )
    fingerprint = fields.Text(
        help="This is the fingerprint that is advertised by this system in"
        " order to validate its identity."
    )
    ignore_fingerprint = fields.Boolean(
        default=True,
        help="Set this to `True` in order to ignore an invalid/unknown"
        " fingerprint from the system.",
    )
    remote_path = fields.Char(
        help="Restrict to this directory path on the remote, if applicable."
    )
    company_ids = fields.Many2many(
        string="Companies",
        comodel_name="res.company",
        required=True,
        default=lambda s: [(6, 0, s.env.user.company_id.ids)],
        help="Access to this system is restricted to these companies.",
    )
    system_type = fields.Selection(
        # Use lambda selection, otherwise subclasses loaded later will not be found.
        selection=lambda self: self._get_system_types(),
        required=True,
    )

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", "Connection name must be unique.")
    ]

    @api.model
    def _get_system_types(self):
        """Return the adapter interface models that are installed."""
        adapter = self.env["external.system.adapter"]
        subclasses = set()
        work = [adapter]
        while work:
            parent = work.pop()
            for child in parent._inherit_children:
                subclass = self.env[child]
                if subclass not in subclasses:
                    subclasses.add(subclass)
                    work.append(subclass)
        return [(m._name, m._description) for m in subclasses]

    @api.multi
    @api.constrains("fingerprint", "ignore_fingerprint")
    def check_fingerprint_ignore_fingerprint(self):
        """Do not allow a blank fingerprint if not set to ignore."""
        for record in self:
            if not record.ignore_fingerprint and not record.fingerprint:
                raise ValidationError(
                    _(
                        "Fingerprint cannot be empty when Ignore Fingerprint is"
                        " not checked."
                    )
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
        adapter = None
        client = None
        try:
            adapter = self._get_adapter()
            client = adapter.external_get_client()
            yield client
        finally:
            if client:
                adapter.external_destroy_client(client)

    @api.multi
    def action_test_connection(self):
        """Test the connection to the external system.

        Any unexpected exception will be transformed into a
        ValidationError. A ValidationError will also be raised
        if no client is returned.
        """
        self.ensure_one()
        try:
            with self.client() as client:
                if client is None:
                    raise ValidationError(
                        _("Client connection failed for system %s") % self.name
                    )
            return True
        except Exception as exc:
            raise ValidationError(
                _("Unexpected error %s when connecting to %s") % (exc, self.name)
            )

    def _get_adapter(self):
        """Trivial method to get adapter from system type.

        Adding the system to the context allows the AbstractModel for the adapter,
        that can not be instantiated, to still hold information, through a class
        property, that can be accessed by all methods in derived classes.

        An alternative would be to use standard python classes, but that would take
        away the possibility to extend them in the Odoo way.
        """
        return self.with_context(system=self).env[self.system_type]
