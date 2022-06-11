# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields

import logging
import xmlrpc

_logger = logging.getLogger()


class ExternalOdooClient:
    """
    Odoo provider for external model
    """

    # Create the client with all credentials needed to connect to external Odoo
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password

    # Implementing search function, returning record ids matching arguments
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

        # Connect to external Odoo server
        common = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url))

        # Calling remote search function
        res = []
        for record in models.execute_kw(
            self.db, uid, self.password, external_name, 'search_read',
            [args],
            {'fields': ['id']}
        ):
            res.append(record['id'])

        return res

    # Implementing select_by_ids function, returning record fields
    def select_by_ids(self, external_name, tenant_id, user, ids, model_fields):

        # Find all fields to get
        fields_to_get = ['id']
        for name, field in model_fields.items():
            if getattr(field, "external", False):
                fields_to_get.append(getattr(field, "external_name", name))

        # Connect to external Odoo server
        common = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url))

        _logger.warning(fields_to_get)

        # Calling remote search_read function
        res = []
        for record in models.execute_kw(
            self.db, uid, self.password, external_name, 'search_read',
            [[['id', 'in', ids]]],
            {'fields': fields_to_get}
        ):
            _logger.warning(record)
            for name, field in model_fields.items():
                if getattr(field, "external", False):
                    # Converting Many2one to only return id
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
                    # Converting One2many to only return id
                    if isinstance(field, fields.One2many):
                        field_name = getattr(field, "external_name", name)
                        if field_name in record:
                            one2many_res = []
                            for nested_id in record[field_name]:
                                one2many_res.append({'id': nested_id})
                            record[field_name] = one2many_res

            res.append(record)

        return res

    # Implementing create function, calling remote create function in
    # external Odoo server
    # pylint: disable=method-require-super
    def create(self, external_name, tenant_id, user, values):

        # Connect to external Odoo server
        common = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(
            self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url))

        # Calling remote create function
        res = models.execute_kw(
            self.db, uid, self.password, external_name, 'create', [values])

        return {'id': res}

    # Implementing update function, calling remote write function in
    # external Odoo server
    def update(
            self, external_name, tenant_id, user,
            record_id, values, model_fields):

        # Connect to external Odoo server
        common = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url))

        for name, field in model_fields.items():
            if getattr(field, "external", False):
                # Converting actions into Odoo format
                if isinstance(field, fields.One2many):
                    field_name = getattr(field, "external_name", name)
                    if field_name in values and values[field_name]:
                        nested_values = []
                        for action in values[field_name]:
                            if action['action'] == 'create':
                                nested_values.append(
                                    [0, False, action['data']])
                            if action['action'] == 'update':
                                nested_values.append(
                                    [1, action['id'], action['data']])
                            if action['action'] == 'delete':
                                nested_values.append(
                                    [2, action['id'], False])
                        values[field_name] = nested_values

        _logger.warning(values)

        # Calling remote write function
        models.execute_kw(
            self.db, uid, self.password, external_name, 'write',
            [[record_id], values])

        return values

    # Implementing delete function, calling remote unlink function in
    # external Odoo server
    def delete(self, external_name, tenant_id, user, record_id):

        # Connect to external Odoo server
        common = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/common'.format(self.url))
        common.version()
        uid = common.authenticate(self.db, self.username, self.password, {})
        models = xmlrpc.client.ServerProxy(
            '{}/xmlrpc/2/object'.format(self.url))

        # Calling remote unlink function
        models.execute_kw(
            self.db, uid, self.password, external_name, 'unlink',
            [record_id])

        return {}
