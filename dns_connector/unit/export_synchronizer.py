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

import logging
from openerp.addons.connector.unit.synchronizer import ExportSynchronizer


_logger = logging.getLogger(__name__)


"""

Exporters for DNS.

In addition to its export job, an exporter has to:

* check in DNS if the record has been updated more recently than the
  last sync date and if yes, delay an import
* call the ``bind`` method of the binder to update the last sync date

"""


class DNSBaseExporter(ExportSynchronizer):

    """ Base exporter for DNS """

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.Environment`
        """
        super(DNSBaseExporter, self).__init__(environment)
        self.binding_id = None
        self.coswin_id = None

    def _get_openerp_data(self):
        """ Return the raw OpenERP data for ``self.binding_id`` """
        return self.session.browse(self.model._name, self.binding_id)

    def run(self, binding_id, *args, **kwargs):
        """ Run the synchronization

        :param binding_id: identifier of the binding record to export
        """
        self.binding_id = binding_id
        self.binding_record = self._get_openerp_data()

        self.coswin_id = self.binder.to_backend(self.binding_id)
        result = self._run(*args, **kwargs)

        self.binder.bind(self.coswin_id, self.binding_id)
        return result

    def _run(self):
        """ Flow of the synchronization, implemented in inherited classes"""
        raise NotImplementedError
