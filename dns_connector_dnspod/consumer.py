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
from openerp.addons.connector.event import (on_record_write,
                                            on_record_create,
                                            on_record_unlink
                                            )
from .unit.export_synchronizer import export_record

_MODEL_NAMES = ('dns.domain', 'dns.record')
_MODEL_NAMES_RECORD = ('dns.record')


@on_record_create(model_names=_MODEL_NAMES)
def create_domain_all_bindings(session, model_name, record_id, fields=None):
    """ Create a job which export all the bindings of a record."""
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    export_record(session, record._model._name, record.id,
                  fields=fields)


@on_record_unlink(model_names=_MODEL_NAMES)
def delete_domain_all_binding(session, model_name, record_id, fields=None):
    """ Create a job which delete all the bindings of a record. """
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    export_record(session, record._model._name, record.id, fields=fields, method='unlink')


@on_record_write(model_names=_MODEL_NAMES_RECORD)
def write_export_all_bindings(session, model_name, record_id, fields=None):
    """ Create a job which export all the bindings of a record."""
    if session.context.get('connector_no_export'):
        return
    model = session.pool.get(model_name)
    record = model.browse(session.cr, session.uid,
                          record_id, context=session.context)
    export_record(session, record._model._name, record.id, fields=fields, method='write')
