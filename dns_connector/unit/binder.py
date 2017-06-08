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

from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.connector.connector import Binder
from ..backend import dns


class DNSPodBinder(Binder):
    """ Generic Binder for DNSPod """


@dns
class DNSPodModelBinder(DNSPodBinder):
    """
    Bindings are done directly on the binding model.

    Binding models are models called ``dns.{normal_model}``,
    like ``dns.record`` or ``dns.domain``.
    They are ``_inherits`` of the normal models and contains
    the DNS ID, the ID of the DNS Backend and the additional
    fields belonging to the DNS instance.
    """
    _model_name = [
        'dns.record',
        'dns.domain'
    ]

    def to_openerp(self, external_id, unwrap=False):
        """ Give the OpenERP ID for an external ID

        :param external_id: external ID for which we want the OpenERP ID
        :param unwrap: if True, returns the openerp_id of the dns_xx record,
                       else return the id (binding id) of that record
        :return: a record ID, depending on the value of unwrap,
                 or None if the external_id is not mapped
        :rtype: int
        """
        binding_ids = self.session.search(
            self.model._name,
            [('dns_id', '=', str(external_id)),
             ('backend_id', '=', self.backend_record.id)])
        if not binding_ids:
            return None
        assert len(binding_ids) == 1, "Several records found: %s" % binding_ids
        binding_id = binding_ids[0]
        if unwrap:
            return self.session.read(self.model._name,
                                     binding_id,
                                     ['openerp_id'])['openerp_id'][0]
        else:
            return binding_id

    def to_backend(self, binding_id):
        """ Give the external ID for an OpenERP ID

        :param binding_id: OpenERP ID for which we want the external id
        :return: backend identifier of the record
        """
        dns_record = self.session.read(
            self.model._name, binding_id, ['dns_id'])
        assert dns_record
        return dns_record['dns_id']

    def bind(self, external_id, binding_id):
        """ Create the link between an external ID and an OpenERP ID and
        update the last synchronization date.

        :param external_id: External ID to bind
        :param binding_id: OpenERP ID to bind
        :type binding_id: int
        """
        # avoid to trigger the export when we modify the `dns_id`
        context = self.session.context.copy()
        context['connector_no_export'] = True
        now_fmt = datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        if external_id:
            state = 'done'
        else:
            state = 'exception'
        self.environment.model.write(
            self.session.cr,
            self.session.uid,
            binding_id,
            {'dns_id': str(external_id),
             'state': state,
             'sync_date': now_fmt},
            context=context)
