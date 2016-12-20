# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from uuid import uuid4

from odoo import _, api, models

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        from elasticsearch import Elasticsearch
        CONNECTORS.append(('elasticsearch', 'Elasticsearch'))
    except ImportError:
        _logger.info('Elasticsearch library not available. Please install '
                     '"elasticsearch" python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to an Elasticsearch data source. """

    _inherit = "base.external.dbsource"

    current_table = None

    @api.multi
    def connection_close_elasticsearch(self, connection):
        return True

    @api.multi
    def connection_open_elasticsearch(self):
        kwargs = {}
        if self.ca_certs:
            kwargs['ca_certs'] = self.ca_certs
            if self.client_cert and self.client_key:
                kwargs.update({
                    'client_cert': self.client_cert,
                    'client_key': self.client_key,
                })
        return Elasticsearch(
            [self.conn_string_full],
            **kwargs
        )

    def browse_elasticsearch(self, doc_id, doc_type='odoo'):
        """ It returns the elasticsearch document. """
        with self.connection_open() as elastic:
            return elastic.get(
                index=self.current_table,
                doc_type=doc_type,
                id=doc_id,
            )

    def create_elasticsearch(self, vals, doc_type='odoo'):
        """ It creates and returns a new document on Elasticsearch """
        return self.update_elasticsearch(vals, uuid4(), doc_type)

    def delete_elasticsearch(self, doc_id, doc_type='odoo'):
        """ It deletes a document from Elasticsearch """
        with self.connection_open() as elastic:
            return elastic.delete(
                index=self.current_table,
                doc_type=doc_type,
                id=doc_id,
            )

    def search_elasticsearch(self, query):
        """ It searches elasticsearch for query and returns results """
        with self.connection_open() as elastic:
            return elastic.search(
                index=self.current_table,
                body={'query': query},
            )

    def update_elasticsearch(self, body, doc_id, doc_type='odoo'):
        """ It creates or updates a document of type on index.

        Params:
            body: (dict) Data to use as the body of the document.
            doc_id: (int) ID of document in Elastic.
            doc_type: (str) Document type.
        Returns:
            (dict) Document from Elasticsearch.
        """
        with self.connection_open() as elastic:
            return elastic.index(
                index=self.current_table,
                doc_type=doc_type,
                id=doc_id,
                body=body,
            )

    # API/Compatibility

    @api.multi
    def execute_elasticsearch(self, query, params, metadata):
        """ It searches Elasticsearch and returns the result.

        This is a compatibility layer for the old API.
        """

        if not params.get('index'):
            raise KeyError(_(
                '"index" is a required key in "params" for Elasticsearch.',
            ))

        self.change_database_elasticsearch(params['index'])
        res = self.search_elasticsearch(query)
        cols = set(row.keys() for row in res) if metadata else []

        return res, cols
