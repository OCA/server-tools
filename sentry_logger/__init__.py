# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import logging
import cgitb

from openerp.tools import config
from openerp.addons.web.controllers.main import Session

_DEFAULT_LOGGING_LEVEL = logging.ERROR

try:
    from .odoo_sentry_client import OdooClient
    from .odoo_sentry_handler import OdooSentryHandler

    root_logger = logging.root

    processors = (
        'raven.processors.SanitizePasswordsProcessor',
        'raven_sanitize_openerp.OpenerpPasswordsProcessor'
    )
    if config.get(u'sentry_dsn'):
        cgitb.enable()
        # Get DSN info from config file or ~/.openerp_serverrc (recommended)
        dsn = config.get('sentry_dsn')
        try:
            level = getattr(logging, config.get('sentry_logging_level'))
        except (AttributeError, TypeError):
            level = _DEFAULT_LOGGING_LEVEL
        # Create Client
        client = OdooClient(
            dsn=dsn,
            processors=processors,
        )
        handler = OdooSentryHandler(client, level=level)
        root_logger.addHandler(handler)
    else:
        msg = u"Sentry DSN not defined in config file"
        if os.environ.get('OCA_RUNBOT'):
            # don't fail the build on runbot for this
            root_logger.info(msg)
        else:
            root_logger.warn(msg)
        client = None

    # Inject sentry_activated to session to display error message or not
    old_session_info = Session.session_info

    def session_info(self, req):
        res = old_session_info(self, req)
        res['sentry_activated'] = bool(client)
        return res

    Session.session_info = session_info
except ImportError:
    pass
