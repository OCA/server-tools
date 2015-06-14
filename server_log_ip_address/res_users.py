# -*- coding: utf-8 -*-
###############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Arche TI Inc. - http://www.archeti.ca
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

from openerp import models
from openerp import SUPERUSER_ID
from openerp.http import request
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def _get_ipaddress(self, cr, uid, context=None):
        if 'HTTP_X_FORWARDED_FOR' in request.httprequest.environ:
            ip_adds = request.httprequest.environ[
                'HTTP_X_FORWARDED_FOR'].split(",")
            ip = ip_adds[0]
        else:
            ip = request.httprequest.environ['REMOTE_ADDR']
        return ip

    def _get_log_info(self, cr, uid, db, login, x_ctx=''):
        msg = "%s from %s using database %s with IP address: %s " \
            % (x_ctx, login, db, self._get_ipaddress(cr, SUPERUSER_ID))
        _logger.info(msg)
        return True

    def _login(self, db, login, password):

        user_id = super(ResUsers, self)._login(db, login, password)
        cr = self.pool.cursor()
        try:
            if user_id:
                self._get_log_info(cr,
                                   SUPERUSER_ID,
                                   db,
                                   login,
                                   x_ctx='Login Successfully')
            else:
                self._get_log_info(cr,
                                   SUPERUSER_ID,
                                   db,
                                   login,
                                   x_ctx='Login Failed')
        except:
            _logger.info("Something went wrong : no cursor !")
        finally:
            cr.close()
        return user_id
