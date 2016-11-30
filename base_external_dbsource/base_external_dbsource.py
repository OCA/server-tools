# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011
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

import os
import logging
import psycopg2
from odoo import models, fields, api,  _
from odoo.exceptions import Warning as UserError
import odoo.tools as tools

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

try:
    import fdb
    CONNECTORS.append(('fdb', 'Firebird'))
except:
    _logger.info('Firebird libraries not available. Please install "fdb"\
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
    - FireBird: host=localhost;database=mydatabase.gdb;user=sysdba;password=%s;
    port=3050;charset=utf8
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
        elif self.connector == 'fdb':
            kwargs = dict([x.split('=') for x in connStr.split(';')])
            conn = fdb.connect(**kwargs)
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

        rows, cols = list(), list()
        for obj in self:
            conn = obj.conn_open()
            if obj.connector in ["sqlite", "mysql", "mssql"]:
                # using sqlalchemy
                cur = conn.execute(sqlquery, sqlparams)
                if metadata:
                    cols = cur.keys()
                rows = [r for r in cur]

            elif obj.connector in ["fdb"]:
                # using other db connectors
                cur = conn.cursor()
                for key in sqlparams:
                    sqlquery = sqlquery.replace('%%(%s)s' % key,
                                                str(sqlparams[key]))

                cur.execute(sqlquery)
                rows = cur.fetchall()
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
        self.ensure_one()
        conn = False
        try:
            conn = self.conn_open()
        except Exception as e:
            raise UserError(_("Connection test failed: \
                    Here is what we got instead:\n %s") % tools.ustr(e))
        finally:
            if conn:
                conn.close()

        # TODO: if OK a (wizard) message box should be displayed
        raise UserError(_("Connection test succeeded: \
                          Everything seems properly set up!"))
