# -*- coding: utf-8 -*-
# ##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
###############################################################################

from psycopg2._psycopg import TransactionRollbackError

from openerp.osv.orm import except_orm
from openerp.osv.osv import except_osv
from openerp.addons.web.session import SessionExpiredException
from raven.handlers.logging import SentryHandler


odoo_exception_black_list = [
    except_orm,
    except_osv,
    SessionExpiredException,
    TransactionRollbackError,
]


class OdooSentryHandler(SentryHandler, object):

    def can_record(self, record):
        if record.exc_info and record.exc_info[0] in odoo_exception_black_list:
            return False
        if record.module == 'osv' and record.msg == 'Uncaught exception':
            return False
        return super(OdooSentryHandler, self).can_record(record)
