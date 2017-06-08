# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (www.openerp.com)
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

import logging
from tools.config import config
#from service import http_server
from service.websrv_lib import HTTPDir, FixSendError, HttpOptions
from BaseHTTPServer import BaseHTTPRequestHandler
from service.http_server import reg_http_service, OpenERPRootProvider
import urlparse
import urllib
import re
import time
from string import atoi
import addons
import log_utils

class RemoteLogHandler(HttpOptions, FixSendError, BaseHTTPRequestHandler):
    verbose = False
    protocol_version = 'HTTP/1.1'
    _HTTP_OPTIONS= { 'Allow' : [ 'GET', 'HEAD', 'OPTIONS'] }

    def handle(self):
        pass

    def finish(self):
        pass

    def get_db_from_path(self, path):
        return True # super-user, no db

    def do_GET(self):
        global _fifo_log_handler
        # (self.path)
        #uri=urllib.unquote(uri)
        #if self.headers.has_key('If-Match'):
        # *-*
        
        num_logs = 50
        
        data = ''
        pos = _fifo_log_handler.get_cur_pos()
        rlen = 0
        for drec in _fifo_log_handler.get_records_fmt(-50, 50):
            data += drec + '\n'
            rlen += 1
        
        self.send_response(200, 'OK')
        self.send_header("Content-Type", 'text/x-log')
        #self.send_header('Connection', 'close')
        self.send_header('Content-Length', len(data) or 0)
        self.end_headers()
        if hasattr(self, '_flush'):
            self._flush()
        
        if self.command != 'HEAD' and data:
            self.wfile.write(data)

    # We are a logging server, so don't let ourselves create entries!
    def log_message(self, format, *args):
        pass
    
    def log_error(self, format, *args):
        # print "RemoteLogHandler:", format % args
        pass
        
    def log_exception(self, format, *args):
        # print "RemoteLogHandler Exception:", format % args
        pass

    def log_request(self, code='-', size='-'):
        pass

_fifo_log_handler = None

try:
    logs_path = config.get_misc('debug', 'remote_logpath', '_logs')
    logs_capacity = config.get_misc('debug', 'remote_log_capacity', '200')
    logs_capacity = int(logs_capacity)
    if logs_path:
        reg_http_service(HTTPDir('/'+logs_path, RemoteLogHandler,
                OpenERPRootProvider(realm="OpenERP Admin", domain='root')))
        logging.getLogger("web-services").info(
                "Registered HTTP remote log server at %s", logs_path)
    
    log = logging.getLogger()
    _fifo_log_handler = log_utils.FIFOHandler(logs_capacity)
    _fifo_log_handler.formatter = log_utils.MachineFormatter()
    log.addHandler(_fifo_log_handler)
except Exception:
    logging.getLogger('web-services').exception("Cannot initialize remote logging:")

#eof