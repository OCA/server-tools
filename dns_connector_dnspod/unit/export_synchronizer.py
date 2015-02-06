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
from openerp.addons.dns_connector.unit.export_synchronizer import DNSBaseExporter
from openerp.addons.dns_connector.connector import get_environment
from openerp.addons.connector.queue.job import job
from openerp.tools.translate import _


class DNSExporter(DNSBaseExporter):

    """ A common flow for the exports to DNS """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(DNSExporter, self).__init__(environment)
        self.binding_record = None

    def _run(self, fields=None, method='create'):
        """ Flow of the synchronization, implemented in inherited classes"""
        assert self.binding_id
        assert self.binding_record
        record = self.mapper.map_record(self.binding_record).values()
        if not record:
            return _('Nothing to export.')
        if method == 'create':
            result = self._create(record)
            if result:
                self.coswin_id = result['id']
        elif method == 'unlink':
            if 'dns.record' in self._model_name:
                record['record_id'] = self.binding_record.dns_id
            elif 'dns.domain' in self._model_name:
                result = self.binding_record.record_ids.unlink()
            self.coswin_id = self._unlink(record)
        elif method == 'write':
            record['record_id'] = self.binding_record.dns_id
            result = self._update(record)
            if result:
                self.coswin_id = result['id']
        return _('Record exported in the CSV on DNS.')

    def _create(self, data):
        """ Create the DNS record """
        return self.backend_adapter.create(data)

    def _unlink(self, data):
        """ Create the DNS record """
        return self.backend_adapter.delete(data)

    def _update(self, data):
        """ Update an DNS record """
        return self.backend_adapter.write(data)


@job
def export_record(session, model_name, binding_id, fields=None, method='create'):
    """ Export a record on DNS """
    record = session.browse(model_name, binding_id)
    env = get_environment(session, model_name, record.backend_id.id)
    exporter = env.get_connector_unit(DNSExporter)
    result = exporter.run(binding_id, fields=fields, method=method)
    return result
