# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Matthieu Dietrich
#    Copyright 2015 Camptocamp SA
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
##############################################################################

import socket
import logging
from openerp.osv import orm, fields
from dateutil import relativedelta
from datetime import datetime

from server_environment import serv_config

_logger = logging.getLogger(__name__)


class FetchmailServer(orm.Model):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    def _get_timeout_conf(self, cursor, uid, ids, name, args, context=None):
        """
        Return configuration
        """
        res = {}
        for fetchmail in self.browse(cursor, uid, ids):
            global_section_name = 'incoming_mail'

            # default vals
            config_vals = {'timeout': "60"}
            if serv_config.has_section(global_section_name):
                config_vals.update(serv_config.items(global_section_name))

            custom_section_name = '.'.join((global_section_name,
                                            fetchmail.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            # convert string value to integer
            if config_vals['timeout']:
                config_vals['timeout'] = int(config_vals['timeout'])
            res[fetchmail.id] = config_vals
        return res

    _columns = {
        'timeout': fields.function(
            _get_timeout_conf,
            method=True,
            string='Timeout',
            type="integer",
            multi='outgoing_mail_config',
            help="Timeout (in seconds)"),
    }

    def connect(self, cr, uid, server_id, context=None):
        connection = super(FetchmailServer, self).connect(
            cr, uid, server_id, context=context)
        server = self.browse(cr, uid, server_id, context)
        # Add timeout on socket
        if server.timeout:
            connection.sock.settimeout(server.timeout)
        return connection
