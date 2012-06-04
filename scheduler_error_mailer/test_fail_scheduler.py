# -*- coding: utf-8 -*-
##############################################################################
#
#    Scheduler error mailer module for OpenERP
#    Copyright (C) 2012 Akretion
#    @author David Beal <bealdavid@gmail.com>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from osv import fields, osv
from tools.translate import _

class test_fail_scheduler(osv.osv_memory):
    _name = "test.fail.scheduler"
    _description = "Test scheduler failure"

    def test_fail(self, cr, uid, context=None):
        """ This a test fail, only for debugging purpose
            DO NOT UNCOMMENT IMPORT IN init.py IN PRODUCTION ENVIRONNEMENT
        """

        raise osv.except_osv(_('Error :'), _("task failure"))
        # context['tytytyty']

test_fail_scheduler()
