# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Authors: Liu Lixia, Augustin Cisterne-Kaas
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

from openerp.addons.dns_connector.unit.backend_adapter import DNSAdapter
import urllib
import httplib
import json


class DNSPodAdapter(DNSAdapter):
    """ External Records Adapter for DNSPod """

    def __init__(self, environment):
        """

        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(DNSAdapter, self).__init__(environment)

    def create(self, data):
        return self._call('%s.Create' % self._dns_model, data)

    def write(self, data):
        """ Update records on the external system """
        return self._call('%s.Modify' % self._dns_model, data)

    def delete(self, data):
        """ Delete a record on the external system """
        return self._call('%s.Remove' % self._dns_model, data)

    def _call(self, action, arguments):
        """Send request to 'dnsapi.cn'"""
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/json"
        }
        try:
            conn = httplib.HTTPSConnection("dnsapi.cn")
            conn.request('POST', '/%s' % action, urllib.urlencode(arguments), headers)
        except:
            raise
        response = conn.getresponse()
        data = response.read()
        conn.close()
        data_json = json.loads(data)
        if 'domain' in data_json:
            data_json['id'] = data_json['domain']['id']
        elif 'record' in data_json:
            data_json['id'] = data_json['record']['id']
        if response.status == 200 and int(data_json['status']['code']) == 1:
            return data_json
        else:
            return None
