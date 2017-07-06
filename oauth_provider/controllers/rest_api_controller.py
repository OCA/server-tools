# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import http, _

from ..exceptions import OauthApiException
from .oauth_mixin import OauthMixin

_logger = logging.getLogger(__name__)


class RestApiController(OauthMixin):

    API_VERSION = '1.0'

    @http.route(
        '/api/rest/%s/<string:model>' % API_VERSION,
        type='json',
        auth='none',
        methods=['GET'],
    )
    def rest_list(self, access_token, model, domain=None, *a, **kw):
        """ Return allowed information from all records.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            domain (list, optional): Domain to apply to the search, in the
                standard Odoo format. This will be appended to the scope's
                pre-existing filter.

        Returns:
            list of dicts: List of data mappings matching query.
        """
        token = self._validate_token(access_token)
        self._validate_model(model)
        data = token.get_data(model, domain=domain)
        return data

    @http.route(
        '/api/rest/%s/<string:model>/<int:record_id>' % API_VERSION,
        type='json',
        auth='none',
        methods=['GET'],
    )
    def rest_read(self, access_token, model, record_id, *a, **kw):
        """ Return allowed information from specific records.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            record_id (int): ID of record to get.
        """
        token = self._validate_token(access_token)
        self._validate_model(model)
        data = token.get_data(model, [record_id])
        return data

    @http.route(
        '/api/rest/%s/<string:model>' % API_VERSION,
        type='json',
        auth='none',
        methods=['POST'],
    )
    def rest_create(self, access_token, model, *args, **kwargs):
        """ Create and return new record.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            kwargs (mixed): All other named arguments are used as the data
                for record mutation.

        Returns:
            dict: Newly created record data.
        """
        token = self._validate_token(access_token)
        self._validate_model(model)
        record = token.create_record(model, kwargs)
        return token.get_data(model, record.ids)

    @http.route(
        ['/api/rest/%s/<string:model>/<int:record_id>' % API_VERSION,
         '/api/rest/%s/<string:model>/' % API_VERSION,
         ],
        type='json',
        auth='none',
        methods=['PUT'],
    )
    def rest_write(self, access_token, model, record_id=None,
                   record_ids=None, *args, **kwargs):
        """ Modify the defined records and return the newly modified data.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            record_id (int): ID of record to mutate (provided as route
                argument).
            record_ids (list of ints): IDs of record to mutate (provided as
                PUT argument).
            kwargs (mixed): All other named arguments are used as the data
                for record mutation.

        Returns:
            list of dicts: Newly modified record data.
        """

        record_ids = self._get_record_ids(record_id, record_ids)
        token = self._validate_token(access_token)
        self._validate_model(model)
        record = token.write_record(model, record_ids, kwargs)
        return token.get_data(model, record.ids)

    @http.route(
        ['/api/rest/%s/<string:model>/<int:record_id>' % API_VERSION,
         '/api/rest/%s/<string:model>/' % API_VERSION,
         ],
        type='json',
        auth='none',
        methods=['DELETE'],
    )
    def data_delete(self, access_token, model, record_id=None,
                    record_ids=None, *args, **kwargs):
        """ Delete the defined records.

        Args:
            access_token (str): OAuth2 access token to utilize for the
                operation.
            model (str): Name of model to operate on.
            record_id (int): ID of record to mutate (provided as route
                argument).
            record_ids (list of ints): IDs of record to mutate (provided as PUT
                argument).

        Returns:
            bool
        """

        record_ids = self._get_record_ids(record_id, record_ids)
        token = self._validate_token(access_token)
        self._validate_model(model)
        token.delete_record(model, record_ids)

        return True

    def _get_record_ids(self, record_id, record_ids):
        if record_ids is None:
            record_ids = []
        if record_id is not None:
            record_ids.append(record_id)

        if not record_ids:
            raise OauthApiException(_(
                'No record ID was defined. You can define a record ID by '
                'appending it to the end of the route, or including a '
                '`record_ids` argument in the `PUT` data, which is a list '
                'of record IDs to mutate.',
            ))

        return record_ids
