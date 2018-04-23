# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import threading
import smtplib
import logging

from openerp import models

connections_cache = threading.local()

_logger = logging.getLogger(__name__)


class SMTPNoQuit(smtplib.SMTP):
    """ Overrides quit() to prevent Odoo from closing the connection """
    def quit(self):
        pass


class SMTPSSLNoQuit(smtplib.SMTP_SSL):
    """ Overrides quit() to prevent Odoo from closing the connection """
    def quit(self):
        pass


class IrMailServer(models.Model):

    _inherit = 'ir.mail_server'

    def connect(self, host, port, user=None, password=None,
                encryption=False, smtp_debug=False):
        if getattr(connections_cache, 'connections', None) is None:
            connections_cache.connections = {}
        key = (host, port, user)
        connection = connections_cache.connections.get(key)
        if connection:
            try:
                # reset session, also serves to test connection
                connection.rset()
                return connection
            except smtplib.SMTPException:
                _logger.info("Existing SMTP connection is unusable")
        _logger.info("Creating new SMTP connection")
        connection = super(IrMailServer, self).connect(
            host, port, user=user, password=password, encryption=encryption,
            smtp_debug=True)
        if connection.__class__ is smtplib.SMTP:
            connection.__class__ = SMTPNoQuit
        elif connection.__class__ is smtplib.SMTP_SSL:
            connection.__class__ = SMTPSSLNoQuit
        connections_cache.connections[key] = connection
        return connection
