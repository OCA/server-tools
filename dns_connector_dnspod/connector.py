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
from openerp.addons.connector.connector import install_in_connector
from openerp.addons.dns_connector.connector import DNSConnectorInstalled


install_in_connector()


class DNSConnectorDnspodInstalled(DNSConnectorInstalled):
    """Empty model used to know if the module is installed on the
    database.

    If the model is in the registry, the module is installed.
    """
    _name = 'dns_connector_dnspod.installed'
