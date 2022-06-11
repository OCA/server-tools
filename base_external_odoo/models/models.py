# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

import logging
# import jwt
# import os
import xmlrpc

_logger = logging.getLogger()

# class odoo-admin(models.Model):
#     _name = 'odoo-admin.odoo-admin'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class ExternalOdooClient:

    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password

    def search(
            self,
            external_name,
            tenant_id,
            user,
            args,
            offset=0,
            limit=None,
            order=None,
            count=False,
            access_rights_uid=False):

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

        res = []
        for record in models.execute_kw(
            self.db, uid, self.password, external_name, 'search_read',
            [args],
            {'fields': ['id']}
        ):
            res.append(record['id'])

        return res

    def select_by_ids(self, external_name, tenant_id, user, ids, model_fields):

        fields_to_get = ['id']
        for name, field in model_fields.items():
            if getattr(field, "external", False):
                fields_to_get.append(getattr(field, "external_name", name))

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

        _logger.warning(fields_to_get)

        res = []
        for record in models.execute_kw(
            self.db, uid, self.password, external_name, 'search_read',
            [[['id', 'in', ids]]],
            {'fields': fields_to_get}
        ):
            _logger.warning(record)
            for name, field in model_fields.items():
                if getattr(field, "external", False):
                    if isinstance(field, fields.Many2one):
                        field_name = getattr(field, "external_name", name)
                        if field_name in record and record[field_name]:
                            if record[field_name]:
                                one2many_res = []
                                for nested_id in record[field_name]:
                                    one2many_res.append({'id': nested_id})
                                record[field_name] = record[field_name][0]
                            else:
                                record[field_name] = False
                    if isinstance(field, fields.One2many):
                        field_name = getattr(field, "external_name", name)
                        if field_name in record:
                            one2many_res = []
                            for nested_id in record[field_name]:
                                one2many_res.append({'id': nested_id})
                            record[field_name] = one2many_res

            res.append(record)

        return res

    def create(self, external_name, tenant_id, user, values):

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

        res = models.execute_kw(
            self.db, uid, self.password, external_name, 'create', [values])

        return {'id': res}

    def update(self, external_name, tenant_id, user, id, values, model_fields):

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

        for name, field in model_fields.items():
            if getattr(field, "external", False):
                if isinstance(field, fields.One2many):
                    field_name = getattr(field, "external_name", name)
                    if field_name in values and values[field_name]:
                        nested_values = []
                        for action in values[field_name]:
                            if action['action'] == 'create':
                                nested_values.append([0, False, action['data']])
                            if action['action'] == 'update':
                                nested_values.append([1, action['id'], action['data']])
                            if action['action'] == 'delete':
                                nested_values.append([2, action['id'], False])
                        values[field_name] = nested_values

        _logger.warning(values)

        models.execute_kw(
            self.db, uid, self.password, external_name, 'write',
            [[id], values])

        return values

    def delete(self, external_name, tenant_id, user, id):

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(self.url))

        models.execute_kw(
            self.db, uid, self.password, external_name, 'unlink',
            [id])

        return {}
