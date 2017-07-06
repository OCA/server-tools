# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime
import dateutil
import time
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

from ..exceptions import OauthScopeValidationException


class OauthProviderScope(models.Model):
    _name = 'oauth.provider.scope'
    _description = 'OAuth Provider Scope'

    name = fields.Char(
        required=True, translate=True,
        help='Name of the scope, displayed to the user.')
    code = fields.Char(
        required=True, help='Code of the scope, used in OAuth requests.')
    description = fields.Text(
        required=True, translate=True,
        help='Description of the scope, displayed to the user.')
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True,
        help='Model allowed to be accessed by this scope.')
    model = fields.Char(
        related='model_id.model', string='Model Name', readonly=True,
        help='Name of the model allowed to be accessed by this scope.')
    filter_id = fields.Many2one(
        comodel_name='ir.filters', string='Filter',
        domain="[('model_id', '=', model)]",
        help='Filter applied to retrieve records allowed by this scope.')
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields', string='Fields',
        domain="[('model_id', '=', model_id)]",
        help='Fields allowed by this scope.')

    _sql_constraints = [
        ('code_unique', 'UNIQUE (code)',
         'The code of the scopes must be unique !'),
    ]

    @property
    @api.model
    def ir_filter_eval_context(self):
        """ Returns the base eval context for ir.filter domains evaluation """
        return {
            'datetime': datetime,
            'dateutil': dateutil,
            'time': time,
            'uid': self.env.uid,
            'user': self.env.user,
        }

    @api.multi
    def filter_by_model(self, model):
        """ Return the current scopes that are associated to the model.

        Args:
            model (str or BaseModel): Name or object of the model to operate
                on.

        Returns:
            OauthProviderScope: Recordsets associated to the model.
        """
        if isinstance(model, models.BaseModel):
            model = model._name
        return self.filtered(lambda record: record.model == model)

    @api.multi
    def get_data(self, model_name, record_ids=None, all_scopes_match=False,
                 domain=None):
        """ Return the data matching the scopes from the requested model.

        Args:
            model_name (str): Name of the model to operate on.
            record_ids (list[int]): ID of record(s) to find. Will only return
                this record, if defined.
            all_scopes_match (bool): True to filter out records that do not
                match all of the scopes in the current recordset.
            domain (list of tuples, optional): Domain to append to the
                `filter_domain` that is defined in the scope.

        Returns:
            dict:
                This will be a dictionary of scoped record data, keyed by
                record ID.
                If `record_ids` is defined, and only one ID, the inner data
                dictionary will be returned without nesting.
        """

        data = defaultdict(dict)
        eval_context = self.ir_filter_eval_context
        all_scopes_records = self.env[model_name]
        record_ids = record_ids or []

        for scope in self.filter_by_model(model_name):

            records = scope._get_scoped_records(
                model_name, eval_context, domain, record_ids,
            )

            for record_data in records.read(scope.field_ids.mapped('name')):
                for field, value in record_data.items():
                    if isinstance(value, tuple):
                        # Return only the name for a many2one
                        data[record_data['id']][field] = value[1]
                    else:
                        data[record_data['id']][field] = value

            # Keep a list of records that match all scopes
            if not all_scopes_records:
                all_scopes_records = records
            else:
                all_scopes_records &= records

        # If all scopes are required to match, filter the results to keep only
        # those matching all scopes
        if all_scopes_match:
            data = dict(
                filter(
                    lambda _data: _data[0] in all_scopes_records.ids,
                    data.items(),
                ),
            )

        matched_records = {
            rec_id: data.get(rec_id, {}) for rec_id in record_ids
        }
        if matched_records:
            if len(matched_records) == 1:
                return matched_records.values()[0]
            return matched_records

        return data

    @api.multi
    def create_record(self, model_name, vals):
        """ Create a record, validate the scope, and return (if valid).

        Args:
            model_name (str): Name of the model to operate on.
            vals (dict): Values to create record with, keyed by field name.

        Returns:
            OauthProviderScope: Newly created record

        Raises:
            OauthScopeValidationException: If fields are included in vals,
                but are not within the current scope.
        """

        if not self._validate_scope_field(model_name, vals):
            raise OauthScopeValidationException('field')

        record = self.env[model_name].create(vals)

        if not self._validate_scope_record(record):
            raise OauthScopeValidationException('record')

        return record

    def get_record(self, model_name, domain=None):
        """ Get the currently scoped records, adhering to optional domain.

        Args:
            model_name (str): Model to search.
            domain (list of tuples, optional): Additional domain to add to the
                currently scoped filter.

        Returns:
            BaseModel: Recordsets.
        """
        records = self.env[model_name]
        eval_context = self.ir_filter_eval_context
        for scope in self.filter_by_model(model_name):
            records += scope._get_scoped_records(
                model_name, eval_context, domain,
            )
        return records

    @api.multi
    def write_record(self, records, vals):
        """ Write to a recordset, adhering to the current scope.

        Args:
            records (BaseModel): Recordset to write to.
            vals (dict): Values to modify records with, keyed by field name.

        Returns:
            OauthProviderScope: The same recordset that was provided as input.

        Raises:
            OauthScopeValidationException: Raised in the following cases:
                * If records are attempted to be edited, but are not within
                    the current scope.
                * If fields are included in vals, but are not within the
                    current scope.
                * If the record no longer falls within scope after being
        """

        if not self._validate_scope_field(records._name, vals):
            raise OauthScopeValidationException('field')

        if not self._validate_scope_record(records):
            raise OauthScopeValidationException('record')

        records.write(vals)

        if not self._validate_scope_record(records):
            raise OauthScopeValidationException('record')

        return records

    @api.multi
    def delete_record(self, records):
        """ Delete a recordset that is within the current scope.

        Args:
            records (BaseModel): Recordset to delete.

        Raises:
            OauthScopeValidationException: If records are not within the
                current scope.
        """

        if not self._validate_scope_record(records):
            raise OauthScopeValidationException('record')

        records.unlink()

    @api.multi
    def _get_filter_domain(self, eval_context, record_ids=None):
        """ Return the scope's domain.

        Args:
            eval_context (dict): Base eval context, such as provided by
                `ir_filter_eval_context`
            record_ids (list[ints], optional): ID of record(s) to explicitly
                query.

        Returns:
            list of tuples: Domain of the scope, in standard Odoo format.
        """

        self.ensure_one()

        if record_ids is None:
            record_ids = []

        filter_domain = [(1, '=', 1)]

        if self.filter_id:
            filter_domain = safe_eval(
                self.filter_id.sudo().domain,
                eval_context,
            )

        if record_ids:
            filter_domain.append(
                ('id', 'in', record_ids),
            )

        return filter_domain

    @api.multi
    def _get_scoped_records(self, model_name, eval_context=None,
                            add_domain=None, record_ids=None):
        """ Return records that are within the scopes in the recordset.

        Args:
            model_name (str): Name of model to operate on.
            eval_context (dict, optional): Base eval context, such as provided
                by `ir_filter_eval_context`.
            add_domain (list of tuples, optional): Domain to append to the
                `filter_domain` that is defined in the scope.
            record_ids (list[int], optional): ID of record to find. Will
                only return this record, if defined.

        Returns:
            BaseModel: Recordset matching the scope.
        """

        self.ensure_one()
        if eval_context is None:
            eval_context = self.ir_filter_eval_context
        if add_domain is None:
            add_domain = []
        filter_domain = self._get_filter_domain(eval_context, record_ids)
        return self.env[model_name].search(filter_domain + add_domain)

    @api.multi
    def _validate_scope_record(self, records):
        """ Validate that the recordset is within the current scope.

        Args:
            records (BaseModel): Recordset to validate.

        Returns:
            bool: Indicating whether the records are within scope.
        """

        scoped_records = self.env[records._name]
        for scope in self:
            scoped_records |= scope._get_scoped_records(
                records._name,
            )
        return all([
            r in scoped_records for r in records
        ])

    @api.multi
    def _validate_scope_field(self, model, vals):
        """ Validate that the input vals do not violate the current scope.

        If there are no fields defined in the scope, all fields are assumed to
        be permitted.

        Args:
            model (BaseModel): Name of the model to operate on.
            vals (dict): Values that should be checked against the current
                scope, keyed by field name.

        Returns:
            bool: Whether the values are within the scope.
        """
        scopes = self.filter_by_model(model)
        field_names = scopes.mapped('field_ids.name')
        if not field_names:
            return True
        return all([
            f in field_names for f in vals.keys()
        ])
