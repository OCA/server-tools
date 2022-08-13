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
from osv import fields, osv
from openerp.tools.translate import _
import openerp.tools as tools
import logging
_logger = logging.getLogger(__name__)

CONNECTORS = []

try:
    import sqlalchemy
    import pymssql 
    CONNECTORS.append( ('mssql', 'Microsoft SQL Server') )
except:
        _logger.info('MS SQL Server not available. Please install "slqalchemy" and "pymssql" python package.')

try:
    import sqlalchemy
    import MySQLdb
    CONNECTORS.append( ('mysql', 'MySQL') )
except:
    _logger.info('MySQL not available. Please install "slqalchemy" and "mysqldb" python package.')

try:
    import pyodbc
    CONNECTORS.append( ('pyodbc', 'ODBC') )
except:
    _logger.info('ODBC libraries not available. Please install "unixodbc" and "python-pyodbc" packages.')

try:
    import cx_Oracle
    CONNECTORS.append( ('cx_Oracle', 'Oracle') )
except:
    _logger.info('Oracle libraries not available. Please install "cx_Oracle" python package.')

import psycopg2
CONNECTORS.append( ('postgresql', 'PostgreSQL') )

try:
    import sqlalchemy
    CONNECTORS.append( ('sqlite', 'SQLite') )
except:
    _logger.info('SQLAlchemy not available. Please install "slqalchemy" python package.')
 
class base_external_dbsource(osv.osv):
    _name = "base.external.dbsource"
    _description = 'External Database Sources'
    _columns = {
        'name': fields.char('Datasource name', required=True, size=64),
        'conn_string': fields.text('Connection string', help="""\
Sample connection strings:
- Microsoft SQL Server: mssql+pymssql://username:%s@server:port/dbname?charset=utf8
- MySQL: mysql://user:%s@server:port/dbname
- ODBC: DRIVER={FreeTDS};SERVER=server.address;Database=mydb;UID=sa
- ORACLE: username/%s@//server.address:port/instance
- PostgreSQL: dbname='template1' user='dbuser' host='localhost' port='5432' password=%s
- SQLite: sqlite:///test.db
"""),
        'password': fields.char('Password' , size=40),
        'connector': fields.selection(CONNECTORS, 'Connector', required=True,
            help = "If a connector is missing from the list, check the " \
                 + "server log to confirm that the required componentes were detected."),
    }

    def conn_open(self, cr, uid, id1):
        #Get dbsource record
        data = self.browse(cr, uid, id1)
        #Build the full connection string
        connStr = data.conn_string
        if data.password:
            if '%s' not in data.conn_string:
                connStr += ';PWD=%s'
            connStr = connStr % data.password
        #Try to connect
        if data.connector == 'cx_Oracle':
            os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
            conn = cx_Oracle.connect(connStr)
        elif data.connector == 'pyodbc':
            conn = pyodbc.connect(connStr)
        elif data.connector in ('sqlite','mysql','mssql'):
            conn = sqlalchemy.create_engine(connStr).connect()
        elif data.connector == 'postgresql':
            conn = psycopg2.connect(connStr)

        return conn

    def execute_and_inspect(self, cr, uid, ids, sqlquery, sqlparams=None, context=None):
        """Executes SQL and returns a dict with the rows and the list of columns.
        
            "sqlparams" can be a dict of values, that can be referenced in the SQL statement
            using "%(key)s" or, in the case of Oracle, ":key".
            Example: 
                sqlquery = "select * from mytable where city = %(city)s and date > %(dt)s"
                params   = {'city': 'Lisbon', 'dt': datetime.datetime(2000, 12, 31)}
                
            Sample result:  { 'colnames'; ['col_a', 'col_b', ...]
                            , 'rows': [ (a0, b0, ...), (a1, b1, ...), ...] }
        """
        data = self.browse(cr, uid, ids)
        nams = dict()
        rows = list()
        for obj in data:
            conn = self.conn_open(cr, uid, obj.id)
            if obj.connector in ["sqlite","mysql","mssql"]: 
                #using sqlalchemy
                cur = conn.execute(sqlquery, sqlparams)
                nams = cur.keys()
                rows = [r for r in cur]
            else: 
                #using other db connectors
                cur = conn.cursor()
                cur.execute(sqlquery, sqlparams)
                nams = [d[0] for d in cur.description]
                rows = cur.fetchall()
            conn.close()
        return {'colnames': nams, 'rows': rows}

    def execute(self, cr, uid, ids, sqlquery, sqlparams=None, context=None):
        return self.execute_and_inspect(self, cr, uid, ids, sqlquery, sqlparams)['rows']
        
    def connection_test(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context):
            conn = False
            try:
                conn = self.conn_open(cr, uid, obj.id)
            except Exception, e:
                raise osv.except_osv(_("Connection test failed!"), _("Here is what we got instead:\n %s") % tools.ustr(e))
            finally:
                try:
                    if conn: conn.close()
                except Exception:
                    # ignored, just a consequence of the previous exception
                    pass
        #TODO: if OK a (wizard) message box should be displayed
        raise osv.except_osv(_("Connection test succeeded!"), _("Everything seems properly set up!"))
    
base_external_dbsource()
