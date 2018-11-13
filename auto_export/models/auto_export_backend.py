# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, _
from openerp.addons.connector.session import ConnectorSession
from .auto_export_connector_checkpoint import add_checkpoint as \
    auto_export_add_checkpoint

_logger = logging.getLogger(__name__)


class AutoExportBackend(models.Model):
    _name = 'auto.export.backend'
    _inherit = 'connector.backend'
    _description = "Auto Export Backend"

    version = fields.Selection(
        selection_add=[('1', '1.0')]
    )

    @api.multi
    def add_checkpoint(self, record, description):
        self.ensure_one()
        session = ConnectorSession.from_env(self.sudo().env)
        auto_export_add_checkpoint(
            session, record._name, record.id, self._name, self.id, description)

    @api.model
    def get_backend(self):
        domain = [(1, '=', 1)]
        backend = self.search(domain)
        if len(backend) != 1:
            raise ValueError(_('No backend found'))
        return backend

    @api.multi
    def log_auto_export_action(self, msg, record, log_level='info'):
        """
        This method logs the auto export action.
        :param msg: custom message to log
        :param record: source auto.export record
        :param log_level: info, warn of error
        """
        message = _("Auto Export {display_name}: {msg}").format(
            display_name=record.display_name, msg=msg)
        if log_level == 'error':
            _logger.error(message)
        elif log_level == 'warn':
            _logger.warning(message)
        else:
            _logger.info(message)

    @api.multi
    def process_auto_export_exception(self, record, e):
        """
        This method logs the error and creates a checkpoint on the record.
        :param record: auto.export record
        :param e: raised exception to log
        """
        _logger.exception(_("Auto Export Error (display_name)").format(
            display_name=record.display_name))
        self.add_checkpoint(record, repr(e))
