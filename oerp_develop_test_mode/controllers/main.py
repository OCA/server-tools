# -*- coding: utf-8 -*-
##############################################################################
#
#    BizzAppDev
#    Copyright (C) 2004-TODAY bizzappdev(<http://www.bizzappdev.com>).
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


from openerp.addons.web import http
from openerp.tools import config
import openerp
import os
import urllib
import urlparse
import re
openerpweb = http
from web.controllers.main import Binary


def db_monodb(req):
    # if only one db exists, return it else return False
    return db_redirect(req, True)[0]


def db_redirect(req, match_first_only_if_unique):
    db = False
    redirect = False

    # 1 try the db in the url
    db_url = req.params.get('db')
    if db_url:
        return (db_url, False)

    dbs = db_list(req, True)

    # 2 use the database from the cookie if it's listable and still listed
    cookie_db = req.httprequest.cookies.get('last_used_database')
    if cookie_db in dbs:
        db = cookie_db

    # 3 use the first db if user can list databases
    if dbs and not db and (not match_first_only_if_unique or len(dbs) == 1):
        db = dbs[0]

    # redirect to the chosen db if multiple are available
    if db and len(dbs) > 1:
        query = dict(urlparse.parse_qsl(req.httprequest.query_string,
                                        keep_blank_values=True))
        query.update({'db': db})
        redirect = req.httprequest.path + '?' + urllib.urlencode(query)
    return (db, redirect)


def db_list(req, force=False):
    proxy = req.session.proxy("db")
    dbs = proxy.list(force)
    h = req.httprequest.environ['HTTP_HOST'].split(':')[0]
    d = h.split('.')[0]
    r = openerp.tools.config['dbfilter'].replace('%h', h).replace('%d', d)
    dbs = [i for i in dbs if re.match(r, i)]
    return dbs


class mode(openerpweb.Controller):
    _cp_path = "/web/mode"

    @openerpweb.jsonrequest
    def get_mode(self, req, mode=False, db=False):
        if not db:
            dbs = db_list(req)
            db = dbs and dbs[0] or False
        return config.get(mode, {}).get(db, False)


class cp_Binary(Binary):
    _cp_path = "/web/binary"

    @openerpweb.httprequest
    def company_logo(self, req, dbname=None):
        if req.session._db:
            dbname = req.session._db
        elif dbname is None:
            dbname = db_monodb(req)

        mode = config.get('develop', {}).get(dbname,
                                             False) and 'develop' or False
        mode = not mode and config.get('test',
                                       {}).get(dbname,
                                               False) and 'test' or mode
        if not mode:
            return super(cp_Binary, self).company_logo(req, dbname=dbname)

        # TODO add etag, refactor to use /image code for etag
        module_path = list(os.path.split(__file__)[:-1]) + ["%s_logo.png" %
                                                            mode]
        image = open(os.path.join(*module_path), 'r')
        image_data = image.read()
        image.close()
        headers = [
            ('Content-Type', 'image/png'),
            ('Content-Length', len(image_data)),
        ]
        return req.make_response(image_data, headers)
