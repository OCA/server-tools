# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from datetime import datetime
from odoo import models, fields, api

import logging
_logger = logging.getLogger()


class WebExternalModel(models.AbstractModel):
    """
    Abstract model to inherit if you want a model to be linked to
    an external API.

    This will override all CRUD functions to call the _external_client
    functions instead of the ORM.
    """

    _name = 'base_external.model'
    _description = 'External model'

    # Specify the provider here, so the model know where to get the data
    _external_client = False

    # Boolean to specify if this model is multi-tenant. This allow us to
    # manage records from several tenants in the same Odoo interface.
    # Record id will then take the form TENANT_ID|RECORD_ID
    _use_tenants = False

    # This code is disabled for now, but we keep it as a reminder that there is
    # some native way to disable the ORM
    # _auto = False

    # # We disable automatic initialisation of model in database
    # @api.model_cr_context
    # def _auto_init(self):
    #     return

    def __init__(self, arg1, arg2):
        # We set by default a fake interface to print warning message
        # if the external_client is not set
        self._external_client = ExternalClientInterface()

    @api.multi
    def _search(
            self,
            args,
            offset=0,
            limit=None,
            order=None,
            count=False,
            access_rights_uid=False):
        """
        Overriding default _search function
        """

        _logger.info('_search %s' % args)

        # If model use tenants, we must have tenant_id in arguments
        # Then we save it for later use, or return empty array
        tenant_id = ""
        if self._use_tenants:
            tenant_id = False
            for arg in args:
                if arg[0] == 'tenant_id':
                    tenant_id = arg[2]

            if not tenant_id:
                return []

        # Get record ids from external_client
        ids = self._external_client.search(
            self._external_name,
            tenant_id,
            self.env.user,
            args,
            offset=offset,
            limit=None,
            order=None,
            count=False)

        _logger.info(ids)

        # If model use tenant, we build the record ids with the tenant_id
        if self._use_tenants:
            newIds = []
            for record_id in ids:
                newIds.append("%s|%s" % (tenant_id, record_id))
            ids = newIds

        return ids

    # pylint: disable=dangerous-default-value
    def _read_from_database(self, field_names, inherited_field_names=[]):
        """
        Overriding default _read_from_database function, to get
        record fields for all record ids
        """

        _logger.info('_read_from_database %s' % field_names)
        _logger.info(self._ids)

        fields_pre = [
            field for field in (
                self._fields[name]
                for name in field_names + inherited_field_names)
            if field.name != 'id'
            # if field.base_field.store and field.base_field.column_type
            if not (field.inherited and callable(field.base_field.translate))
        ]
        _logger.warning('fields_pre %s' % fields_pre)

        # Get default user and attachment, we need them for some fields
        user = self.env['res.users'].browse(1)
        attachment = self.env['ir.attachment'].browse()

        # For model with tenant, split tenant_id and record ids
        tenant_id = ""
        ids = self._ids
        if self._use_tenants:
            newIds = []
            for record_id in ids:
                split = record_id.split("|")
                tenant_id = split[0]
                newIds.append(split[1])

            ids = newIds

        # Build arrays for all fields we'll need to return
        values = {
            "tenant_id": [],
            "create_uid": [],
            "write_uid": [],
            "create_date": [],
            "write_date": [],
            "message_main_attachment_id": [],
        }
        for name, field in self._fields.items():
            if getattr(field, "external", False):
                values[name] = []

        # Get data from external client
        fetchIds = []
        results = []
        for result in self._external_client.select_by_ids(
                self._external_name, tenant_id,
                self.env.user, ids, self._fields):

            id = result["id"]
            if self._use_tenants:
                id = "%s|%s" % (tenant_id, id)
            fetchIds.append(id)

            results.append(result)

        # Get odoo objects for all ids
        fetched = self.browse(fetchIds)

        # Assign data in fields arrays, depending of field type
        i = 0
        # Iterating all records returned by external_client
        for result in results:

            # Iterating all fields in current model
            for name, field in self._fields.items():
                # Check whether this field is an external field
                if getattr(field, "external", False):
                    # Tenant ID is special case
                    # we get it's value from record id
                    if name == "tenant_id" and self._use_tenants:
                        tenant = [result['id'].split("|")[0]]
                        tenant = fetched[i]._prefetch[
                            self._fields["tenant_id"].comodel_name
                        ].update(tenant) or tenant
                        values["tenant_id"].append(tenant)
                    # Managing Many2one case, we need to call _prefetch
                    # function with the record id for this to work
                    elif isinstance(field, fields.Many2one):
                        relation_id = result[
                            getattr(field, "external_name", False) or name
                        ]
                        if getattr(
                            self.env[field.comodel_name],
                            "_use_tenants", False
                        ):
                            relation_id = "%s|%s" % (
                                tenant_id, relation_id)
                        if relation_id:
                            prefetch_ids = [relation_id]
                            prefetch_ids = fetched[i]._prefetch[
                                field.comodel_name
                            ].update(prefetch_ids) or prefetch_ids
                            values[name].append(prefetch_ids)
                        else:
                            values[name].append(fetched[i]._prefetch[
                                field.comodel_name
                            ])
                    # Managing One2many case
                    elif isinstance(field, fields.One2many):
                        nested_ids = []
                        for nested in result[
                            getattr(field, "external_name", False) or name
                        ]:
                            if getattr(
                                self.env[field.comodel_name],
                                "_use_tenants", False
                            ):
                                nested['id'] = "%s|%s" % (
                                    tenant_id, nested['id'])
                            nested_ids.append(nested['id'])
                        values[name].append(nested_ids)
                    # Managing One2many case
                    elif isinstance(field, fields.Many2many):
                        _logger.warning(field.name)
                        _logger.warning(field.comodel_name)
                        nested_ids = result[
                            getattr(field, "external_name", False) or name
                        ]
                        if getattr(
                            self.env[field.comodel_name], "_use_tenants", False
                        ):
                            new_ids = []
                            for nested_id in nested_ids:
                                nested_id = "%s|%s" % (
                                    tenant_id, nested_id)
                                new_ids.append(nested_id)
                            nested_ids = new_ids
                        values[name].append(nested_ids)
                    else:
                        values[name].append(result[
                            getattr(field, "external_name", False) or name
                        ])

            # Managing value for some native fields required by Odoo
            values["create_uid"].append(user)
            values["write_uid"].append(user)
            values["create_date"].append(datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT))
            values["write_date"].append(datetime.now().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT))
            values["message_main_attachment_id"].append(attachment)

        _logger.warning('fetched %s' % fetched)
        _logger.warning('fields_pre %s' % fields_pre)

        # Now that the fields arrays are ready, we load their data in
        # cache so Odoo can find them and stop calling _read_from_database
        for field_pre in fields_pre:
            # Loading our custom fields
            for name, field in self._fields.items():
                if getattr(field, "external", False):
                    if field_pre.name == name:
                        _logger.info('%s_values %s' % (name, values[name]))
                        self.env.cache.update(fetched, field_pre, values[name])

            # Loading mandatory native fields
            if field_pre.name == "tenant_id":
                self.env.cache.update(fetched, field_pre, values["tenant_id"])
            if field_pre.name == "create_uid":
                self.env.cache.update(fetched, field_pre, values["create_uid"])
            if field_pre.name == "write_uid":
                self.env.cache.update(fetched, field_pre, values["write_uid"])
            if field_pre.name == "create_date":
                self.env.cache.update(
                    fetched, field_pre, values["create_date"])
            if field_pre.name == "write_date":
                self.env.cache.update(fetched, field_pre, values["write_date"])
            if field_pre.name == "message_main_attachment_id":
                self.env.cache.update(
                    fetched, field_pre,
                    values["message_main_attachment_id"])

        followers_values = []
        for _ in fetched:
            followers_values.append("")

        i = i + 1

    @api.model
    def _create(self, data_list):
        """
        Overriding default _create function, to create record in
        external api instead of Odoo database
        """

        _logger.info('_create %s' % data_list)

        ids = []
        for data in data_list:

            tenant_id = ""
            if self._use_tenants:
                if "tenant_id" not in data["stored"]:
                    raise UserWarning("You need to specify the tenant")
                tenant_id = data["stored"]["tenant_id"]

            # Converting Odoo data in a format easier to use for provider
            for name, field in self._fields.items():

                if field.readonly:
                    continue

                if getattr(field, "external", False) and getattr(
                        field, "external_name", ""):

                    data_field = data["stored"][name]
                    # Converting Many2many format
                    if isinstance(field, fields.Many2many):
                        for nested in data["stored"][name]:
                            if nested[0] == 6:
                                data_field = nested[2]

                    data["stored"][
                        getattr(field, "external_name", "")
                    ] = data_field

            # Calling external_client create function
            result = self._external_client.create(
                self._external_name, tenant_id, self.env.user, data["stored"])

            _logger.info(result)

            # Converting new record id with tenant id if using tenant
            if self._use_tenants:
                result['id'] = "%s|%s" % (tenant_id, result['id'])

            ids.append(result['id'])

        # Converting data into Odoo objects and return them
        records = self.browse(ids)
        for data, record in pycompat.izip(data_list, records):
            data['record'] = record
        return records

    @api.multi
    def _write(self, vals):
        """
        Overriding default _write function, to write record in
        external api instead of Odoo database
        """

        _logger.info(vals)

        if not self:
            return True
        self.check_field_access_rights('write', list(vals))

        # Converting Odoo data in a format easier to use for provider
        for name, field in self._fields.items():
            if getattr(field, "external", False) and getattr(
                    field, "external_name", "") and name in vals:

                data_field = vals[name]
                # Converting One2many format
                if isinstance(field, fields.One2many):
                    data_field = []
                    for nested in vals[name]:
                        if nested[0] == 0:
                            nested_data = {}
                            for nested_name, nested_field in self.env[
                                field.comodel_name
                            ]._fields.items():
                                if getattr(
                                    nested_field, "external", False
                                ) and getattr(
                                    nested_field, "external_name", ""
                                ) and nested_name in nested[2]:
                                    nested_data[getattr(
                                        nested_field, "external_name", ""
                                    )] = nested[2][nested_name]

                            data_field.append({
                                'action': 'create',
                                'data': nested_data,
                            })
                        if nested[0] == 1:
                            nested_data = {}
                            for nested_name, nested_field in self.env[
                                field.comodel_name
                            ]._fields.items():
                                if getattr(
                                    nested_field, "external", False
                                ) and getattr(
                                    nested_field, "external_name", ""
                                ) and nested_name in nested[2]:
                                    nested_data[getattr(
                                        nested_field, "external_name", ""
                                    )] = nested[2][nested_name]

                            data_field.append({
                                'action': 'update',
                                'id': nested[1],
                                'data': nested_data,
                            })
                        if nested[0] == 2:
                            data_field.append({
                                'action': 'delete',
                                'id': nested[1],
                            })

                # Converting Many2many format
                if isinstance(field, fields.Many2many):
                    nested_ids = {}
                    for nested in vals[name]:
                        if nested[0] == 6:
                            for nested_id in nested[2]:
                                nested_ids[nested_id] = nested_id

                        if nested[0] == 0:
                            nested_ids[nested[1]] = nested[1]
                    data_field = list(nested_ids.keys())

                vals[
                    getattr(field, "external_name", "")
                ] = data_field

        for record in self:

            # If using tenant, split tenant_id and record id
            tenant_id = ""
            record_id = record.id
            if self._use_tenants:
                split = record_id.split("|")
                tenant_id = split[0]
                record_id = split[1]

            _logger.info("write vals %s", vals)

            # Calling external_client write function
            self._external_client.update(
                self._external_name, tenant_id, self.env.user,
                record_id, vals, self._fields)

        return True

    # pylint: disable=method-require-super
    @api.multi
    def unlink(self):
        """
        Overriding default unlink function, to delete record in
        external api instead of Odoo database
        """

        for record in self:

            # If using tenant, split tenant_id and record id
            tenant_id = ""
            record_id = record.id
            if self._use_tenants:
                split = record_id.split("|")
                tenant_id = split[0]
                record_id = split[1]

            # Calling external_client delete function
            self._external_client.delete(
                self._external_name, tenant_id, self.env.user, record_id)

        return True


class ExternalClientInterface:
    """
    Default interface for external_client, which raise exception when
    calling CRUD function if _external_client is undefined
    """

    def search(
            self,
            external_name,
            tenant_id,
            user,
            args,
            offset=0,
            limit=None,
            order=None,
            count=False):

        raise Exception('Function is not implemented')

    def select_by_ids(self, external_name, tenant_id, user, ids, fields):

        raise Exception('Function is not implemented')

    # pylint: disable=method-require-super
    def create(self, external_name, tenant_id, values):

        raise Exception('Function is not implemented')

    def update(self, external_name, tenant_id, record_id, values, fields):

        raise Exception('Function is not implemented')

    def delete(self, external_name, tenant_id, record_id):

        raise Exception('Function is not implemented')
