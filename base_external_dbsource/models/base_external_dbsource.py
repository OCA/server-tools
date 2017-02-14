# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
import logging

import psycopg2

from openerp import models, fields, api,  _
from openerp.exceptions import Warning as UserError
import openerp.tools as tools

_logger = logging.getLogger(__name__)

CONNECTORS = []

try:
    import sqlalchemy
    CONNECTORS.append(('sqlite', 'SQLite'))
    try:
        import pymssql
        CONNECTORS.append(('mssql', 'Microsoft SQL Server'))
        assert pymssql
    except (ImportError, AssertionError):
        _logger.info('MS SQL Server not available. Please install "pymssql"\
                      python package.')
    try:
        import MySQLdb
        CONNECTORS.append(('mysql', 'MySQL'))
        assert MySQLdb
    except (ImportError, AssertionError):
        _logger.info('MySQL not available. Please install "mysqldb"\
                     python package.')
except:
    _logger.info('SQL Alchemy not available. Please install "slqalchemy"\
                 python package.')
try:
    import pyodbc
    CONNECTORS.append(('pyodbc', 'ODBC'))
except:
    _logger.info('ODBC libraries not available. Please install "unixodbc"\
                 and "python-pyodbc" packages.')

try:
    import cx_Oracle
    CONNECTORS.append(('cx_Oracle', 'Oracle'))
except:
    _logger.info('Oracle libraries not available. Please install "cx_Oracle"\
                 python package.')

CONNECTORS.append(('postgresql', 'PostgreSQL'))


class BaseExternalDbsource(models.Model):
    _name = "base.external.dbsource"
    _description = 'External Database Sources'
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
    """)
    password = fields.Char('Password', size=40)
    connector = fields.Selection(CONNECTORS, 'Connector', required=True,
                                 help="If a connector is missing from the\
                                      list, check the server log to confirm\
                                      that the required components were\
                                      detected.")

    @api.multi
    def conn_open(self):
        """The connection is open here."""

        self.ensure_one()
        # Get dbsource record
        # data = self.browse(cr, uid, id1)
        # Build the full connection string
        connStr = self.conn_string
        if self.password:
            if '%s' not in self.conn_string:
                connStr += ';PWD=%s'
            connStr = connStr % self.password
        # Try to connect
        if self.connector == 'cx_Oracle':
            os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
            conn = cx_Oracle.connect(connStr)
        elif self.connector == 'pyodbc':
            conn = pyodbc.connect(connStr)
        elif self.connector in ('sqlite', 'mysql', 'mssql'):
            conn = sqlalchemy.create_engine(connStr).connect()
        elif self.connector == 'postgresql':
            conn = psycopg2.connect(connStr)

        return conn

    @api.multi
    def execute(self, sqlquery, sqlparams=None, metadata=False,
                context=None):
        """Executes SQL and returns a list of rows.

            "sqlparams" can be a dict of values, that can be referenced in
            the SQL statement using "%(key)s" or, in the case of Oracle,
            ":key".
            Example:
                sqlquery = "select * from mytable where city = %(city)s and
                            date > %(dt)s"
                params   = {'city': 'Lisbon',
                            'dt': datetime.datetime(2000, 12, 31)}

            If metadata=True, it will instead return a dict containing the
            rows list and the columns list, in the format:
                { 'cols': [ 'col_a', 'col_b', ...]
                , 'rows': [ (a0, b0, ...), (a1, b1, ...), ...] }
        """
        # data = self.browse(cr, uid, ids)
        rows, cols = list(), list()
        for obj in self:
            conn = obj.conn_open()
            if obj.connector in ["sqlite", "mysql", "mssql"]:
                # using sqlalchemy
                cur = conn.execute(sqlquery, sqlparams)
                if metadata:
                    cols = cur.keys()
                rows = [r for r in cur]
            else:
                # using other db connectors
                cur = conn.cursor()
                cur.execute(sqlquery, sqlparams)
                if metadata:
                    cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
            conn.close()
        if metadata:
            return{'cols': cols, 'rows': rows}
        else:
            return rows

    @api.multi
    def connection_test(self):
        """Test of connection."""

        for obj in self:
            conn = False
            try:
                conn = self.conn_open()
            except Exception as e:
                raise UserError(_("Connection test failed: \
                        Here is what we got instead:\n %s") % tools.ustr(e))
            finally:
                try:
                    if conn:
                        conn.close()
                except Exception:
                    # ignored, just a consequence of the previous exception
                    pass
        # TODO: if OK a (wizard) message box should be displayed
        raise UserError(_("Connection test succeeded: \
                          Everything seems properly set up!"))
