# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import psycopg2

from contextlib import contextmanager

from odoo import _, api, fields, models, tools

from ..exceptions import ConnectionFailedError, ConnectionSuccessError

_logger = logging.getLogger(__name__)


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to an external data source

    Classes implementing this interface must provide the following methods
    suffixed with the adapter type. See the method definitions and examples
    for more information:
        * ``connection_open_*``
        * ``connection_close_*``
        * ``execute_*``

    Optional methods for adapters to implement:
        * ``remote_browse_*``
        * ``remote_create_*``
        * ``remote_delete_*``
        * ``remote_search_*``
        * ``remote_update_*``
    """

    _name = "base.external.dbsource"
    _description = 'External Database Sources'

    CONNECTORS = [
        ('postgresql', 'PostgreSQL'),
    ]
    # This is appended to the conn string if pass declared but not detected.
    # Children should declare PWD_STRING_CONNECTOR (such as PWD_STRING_FBD)
    #   to allow for override.
    PWD_STRING = 'PWD=%s;'

    name = fields.Char('Datasource name', required=True, size=64)
    conn_string = fields.Text('Connection string', help="""
    Sample connection strings:
    - Microsoft SQL Server:
      mssql+pymssql://username:%s@server:port/dbname?charset=utf8
    - MySQL: mysql://user:%s@server:port/dbname
    - ODBC: DRIVER={FreeTDS};SERVER=server.address;Database=mydb;UID=sa
    - ORACLE: username/%s@//server.address:port/instance
    - PostgreSQL:
        dbname='template1' user='dbuser' host='localhost' port='5432' \
        password=%s
    - SQLite: sqlite:///test.db
    - Elasticsearch: https://user:%s@localhost:9200
    """)
    conn_string_full = fields.Text(
        readonly=True,
        compute='_compute_conn_string_full',
    )
    password = fields.Char('Password', size=40)
    client_cert = fields.Text()
    client_key = fields.Text()
    ca_certs = fields.Char(
        help='Path to CA Certs file on server.',
    )
    connector = fields.Selection(
        CONNECTORS, 'Connector', required=True,
        help="If a connector is missing from the list, check the server "
             "log to confirm that the required components were detected.",
    )

    current_table = None

    @api.multi
    @api.depends('conn_string', 'password')
    def _compute_conn_string_full(self):
        for record in self:
            if record.password:
                if '%s' not in record.conn_string:
                    pwd_string = getattr(
                        record,
                        'PWD_STRING_%s' % record.connector.upper(),
                        record.PWD_STRING,
                    )
                    record.conn_string += pwd_string
                record.conn_string_full = record.conn_string % record.password
            else:
                record.conn_string_full = record.conn_string

    # Interface

    @api.multi
    def change_table(self, name):
        """ Change the table that is used for CRUD operations """
        self.current_table = name

    @api.multi
    def connection_close(self, connection):
        """ It closes the connection to the data source.

        This method calls adapter method of this same name, suffixed with
        the adapter type.
        """

        method = self._get_adapter_method('connection_close')
        return method(connection)

    @api.multi
    @contextmanager
    def connection_open(self):
        """ It provides a context manager for the data source.

        This method calls adapter method of this same name, suffixed with
        the adapter type.
        """

        method = self._get_adapter_method('connection_open')
        try:
            connection = method()
            yield connection
        finally:
            try:
                self.connection_close(connection)
            except:
                _logger.exception('Connection close failure.')

    @api.multi
    def execute(
        self, query=None, execute_params=None, metadata=False, **kwargs
    ):
        """ Executes a query and returns a list of rows.
            "execute_params" can be a dict of values, that can be referenced
            in the SQL statement using "%(key)s" or, in the case of Oracle,
            ":key".
            Example:
                query = "SELECT * FROM mytable WHERE city = %(city)s AND
                            date > %(dt)s"
                execute_params   = {
                    'city': 'Lisbon',
                    'dt': datetime.datetime(2000, 12, 31),
                }

            If metadata=True, it will instead return a dict containing the
            rows list and the columns list, in the format:
                { 'cols': [ 'col_a', 'col_b', ...]
                , 'rows': [ (a0, b0, ...), (a1, b1, ...), ...] }
        """

        # Old API compatibility
        if not query:
            try:
                query = kwargs['sqlquery']
            except KeyError:
                raise TypeError(_('query is a required argument'))
        if not execute_params:
            try:
                execute_params = kwargs['sqlparams']
            except KeyError:
                pass

        method = self._get_adapter_method('execute')
        rows, cols = method(query, execute_params, metadata)

        if metadata:
            return {'cols': cols, 'rows': rows}
        else:
            return rows

    @api.onchange('connector')
    def _change_placeholder_str_connect(self):
        """
        Changing value of connector field will automatically
        set value in conn_string field.
        """
        if self.connector == 'fdb':
            self.conn_string = "host=localhost;" \
                               "database=mydatabase.gdb;" \
                               "user=sysdba;" \
                               "password=%s;" \
                               "port=3050;" \
                               "charset=none"

        elif self.connector == 'postgresql':
            self.conn_string = "dbname='template1' " \
                               "user='dbuser' " \
                               "host='localhost' " \
                               "port='5432' " \
                               "password=%s"

        elif self.connector == 'cx_Oracle':
            self.conn_string = "username/%s@//server.address:port/instance"

        elif self.connector == 'mysql':
            self.conn_string = "mysql://user:%s@server:port/dbname"

        elif self.connector == 'sqlite':
            self.conn_string = "sqlite:///test.db"

        elif self.connector == 'pyodbc':
            self.conn_string = "DRIVER={FreeTDS};" \
                               "SERVER=server.address;" \
                               "Database=mydb;" \
                               "UID=sa"

        elif self.connector == 'mssql':
            self.conn_string = "mssql+pymssql:" \
                               "//username:%s" \
                               "@server:port/dbname" \
                               "?charset=utf8"

    @api.multi
    def connection_test(self):
        """ It tests the connection

        Raises:
            ConnectionSuccessError: On connection success
            ConnectionFailedError: On connection failed
        """

        for obj in self:
            try:
                with self.connection_open():
                    pass
            except Exception as e:
                raise ConnectionFailedError(_(
                    "Connection test failed:\n"
                    "Here is what we got instead:\n%s"
                ) % tools.ustr(e))
        raise ConnectionSuccessError(_(
            "Connection test succeeded:\n"
            "Everything seems properly set up!",
        ))

    @api.multi
    def remote_browse(self, record_ids, *args, **kwargs):
        """ It browses for and returns the records from remote by ID

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Args:
            record_ids: (list) List of remote IDs to browse.
            *args: Positional arguments to be passed to adapter method.
            **kwargs: Keyword arguments to be passed to adapter method.
        Returns:
            (iter) Iterator of record mappings that match the ID.
        """

        assert self.current_table
        method = self._get_adapter_method('remote_browse')
        return method(record_ids, *args, **kwargs)

    @api.multi
    def remote_create(self, vals, *args, **kwargs):
        """ It creates a record on the remote data source.

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Args:
            vals: (dict) Values to use for creation.
            *args: Positional arguments to be passed to adapter method.
            **kwargs: Keyword arguments to be passed to adapter method.
        Returns:
            (mapping) A mapping of the record that was created.
        """

        assert self.current_table
        method = self._get_adapter_method('remote_create')
        return method(vals, *args, **kwargs)

    @api.multi
    def remote_delete(self, record_ids, *args, **kwargs):
        """ It deletes records by ID on remote

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Args:
            record_ids: (list) List of remote IDs to delete.
            *args: Positional arguments to be passed to adapter method.
            **kwargs: Keyword arguments to be passed to adapter method.
        Returns:
            (iter) Iterator of bools indicating delete status.
        """

        assert self.current_table
        method = self._get_adapter_method('remote_delete')
        return method(record_ids, *args, **kwargs)

    @api.multi
    def remote_search(self, query, *args, **kwargs):
        """ It searches the remote for the query.

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Args:
            query: (mixed) Query domain as required by the adapter.
            *args: Positional arguments to be passed to adapter method.
            **kwargs: Keyword arguments to be passed to adapter method.
        Returns:
            (iter) Iterator of record mappings that match query.
        """

        assert self.current_table
        method = self._get_adapter_method('remote_search')
        return method(query, *args, **kwargs)

    @api.multi
    def remote_update(self, record_ids, vals, *args, **kwargs):
        """ It updates the remote records with the vals

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Args:
            record_ids: (list) List of remote IDs to delete.
            *args: Positional arguments to be passed to adapter method.
            **kwargs: Keyword arguments to be passed to adapter method.
        Returns:
            (iter) Iterator of record mappings that were updated.
        """

        assert self.current_table
        method = self._get_adapter_method('remote_update')
        return method(record_ids, vals, *args, **kwargs)

    # Adapters

    def connection_close_postgresql(self, connection):
        return connection.close()

    def connection_open_postgresql(self):
        return psycopg2.connect(self.conn_string)

    def execute_postgresql(self, query, params, metadata):
        return self._execute_generic(query, params, metadata)

    def _execute_generic(self, query, params, metadata):
        with self.connection_open() as connection:
            cur = connection.cursor()
            cur.execute(query, params)
            cols = []
            if metadata:
                cols = [d[0] for d in cur.description]
            rows = cur.fetchall()
            return rows, cols

    # Compatibility & Private

    @api.multi
    def conn_open(self):
        """ It opens and returns a connection to the remote data source.

        This method calls adapter method of this same name, suffixed with
        the adapter type.

        Deprecate:
            This method has been replaced with ``connection_open``.
        """

        with self.connection_open() as connection:
            return connection

    def _get_adapter_method(self, method_prefix):
        """ It returns the connector adapter method for ``method_prefix``.

        Args:
            method_prefix: (str) Prefix of adapter method (such as
                ``connection_open``).
        Raises:
            NotImplementedError: When the method is not found
        Returns:
            (instancemethod)
        """

        self.ensure_one()
        method = '%s_%s' % (method_prefix, self.connector)

        try:
            return getattr(self, method)
        except AttributeError:
            raise NotImplementedError(_(
                '"%s" method not found, check that all assets are installed '
                'for the %s connector type.'
            )) % (
                method, self.connector,
            )
