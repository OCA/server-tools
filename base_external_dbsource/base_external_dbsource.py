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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.tools as tools


_logger = logging.getLogger(__name__)
CONNECTORS = [('postgresql', 'PostgreSQL')]


try:
    import sqlalchemy
    CONNECTORS.append(('sqlite', 'SQLite'))
    try:
        import pymssql
        CONNECTORS.append(('mssql', 'Microsoft SQL Server'))
        assert pymssql
    except (ImportError, AssertionError):
        _logger.debug('MS SQL Server not available. Please install "pymssql"\
                      python package.')
    try:
        import MySQLdb
        CONNECTORS.append(('mysql', 'MySQL'))
        assert MySQLdb
    except (ImportError, AssertionError):
        _logger.debug('MySQL not available. Please install "mysqldb"\
                     python package.')
except:
    _logger.debug('SQL Alchemy not available. Please install "slqalchemy"\
                 python package.')
try:
    import pyodbc
    CONNECTORS.append(('pyodbc', 'ODBC'))
except:
    _logger.debug('ODBC libraries not available. Please install "unixodbc"\
                 and "python-pyodbc" packages.')

try:
    import cx_Oracle
    CONNECTORS.append(('cx_Oracle', 'Oracle'))
except:
    _logger.debug('Oracle libraries not available. Please install "cx_Oracle"\
                 python package.')


class base_external_dbsource(orm.Model):
    _name = "base.external.dbsource"
    _description = 'External Database Sources'
    _columns = {
        'name': fields.char('Datasource name', required=True, size=64),
        'conn_string': fields.text('Connection string', help="""
Sample connection strings:
- Microsoft SQL Server:
  mssql+pymssql://username:%s@server:port/dbname?charset=utf8
- MySQL: mysql://user:%s@server:port/dbname
- ODBC: DRIVER={FreeTDS};SERVER=server.address;Database=mydb;UID=sa
- ORACLE: username/%s@//server.address:port/instance
- PostgreSQL:
  dbname='template1' user='dbuser' host='localhost' port='5432' password=%s
- SQLite: sqlite:///test.db
"""),
        'password': fields.char('Password', size=40),
        'connector': fields.selection(CONNECTORS, 'Connector',
                                      required=True,
                                      help="If a connector is missing from the\
                                      list, check the server log to confirm\
                                      that the required components were\
                                      detected."),
    }

    def conn_open(self, cr, uid, id1):
        # Get dbsource record
        data = self.browse(cr, uid, id1)
        # Build the full connection string
        connStr = data.conn_string
        if data.password:
            if '%s' not in data.conn_string:
                connStr += ';PWD=%s'
            connStr = connStr % data.password
        # Try to connect
        if data.connector == 'cx_Oracle':
            os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
            conn = cx_Oracle.connect(connStr)
        elif data.connector == 'pyodbc':
            conn = pyodbc.connect(connStr)
        elif data.connector in ('sqlite', 'mysql', 'mssql'):
            conn = sqlalchemy.create_engine(connStr).connect()
        elif data.connector == 'postgresql':
            conn = psycopg2.connect(connStr)

        return conn

    def execute(self, cr, uid, ids, sqlquery, sqlparams=None, metadata=False,
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
        data = self.browse(cr, uid, ids)
        rows, cols = list(), list()
        for obj in data:
            conn = self.conn_open(cr, uid, obj.id)
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

    def connection_test(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            conn = False
            try:
                conn = self.conn_open(cr, uid, obj.id)
            except Exception as e:
                raise orm.except_orm(_("Connection test failed!"),
                                     _("Here is what we got instead:\n %s")
                                     % tools.ustr(e))
            finally:
                try:
                    if conn:
                        conn.close()
                except Exception:
                    # ignored, just a consequence of the previous exception
                    pass
        # TODO: if OK a (wizard) message box should be displayed
        raise orm.except_orm(_("Connection test succeeded!"),
                             _("Everything seems properly set up!"))
