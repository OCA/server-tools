# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import dateutil
import time
from collections import defaultdict
from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval


class OAuthProviderScope(models.Model):
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

    @api.model
    def _get_ir_filter_eval_context(self):
        """ Returns the base eval context for ir.filter domains evaluation """
        return {
            'datetime': datetime,
            'dateutil': dateutil,
            'time': time,
            'uid': self.env.uid,
            'user': self.env.user,
        }

    @api.multi
    def get_data_for_model(self, model, res_id=None, all_scopes_match=False):
        """ Return the data matching the scopes from the requested model """
        data = defaultdict(dict)
        eval_context = self._get_ir_filter_eval_context()
        all_scopes_records = self.env[model]
        for scope in self.filtered(lambda record: record.model == model):
            # Retrieve the scope's domain
            filter_domain = [(1, '=', 1)]
            if scope.filter_id:
                filter_domain = safe_eval(
                    scope.filter_id.sudo().domain, eval_context)
            if res_id is not None:
                filter_domain.append(('id', '=', res_id))

            # Retrieve data of the matching records, depending on the scope's
            # fields
            records = self.env[model].search(filter_domain)
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
        # those mathing all scopes
        if all_scopes_match:
            data = dict(filter(
                lambda record_data: record_data[0] in all_scopes_records.ids,
                data.items()))

        # If a single record was requested, return only data coming from this
        # record
        # Return an empty dictionnary if this record didn't recieve data to
        # return
        if res_id is not None:
            data = data.get(res_id, {})

        return data
