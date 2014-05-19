# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 XCG Consulting (www.xcg-consulting.fr)
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


# Before loading the module, if the analytic_size option is given, check it.
# Its value must be an integer greater or equal to the default value.
from openerp.tools import config
try:
    analytic_size = int(config.get_misc('analytic', 'analytic_size', 5))
    assert analytic_size > 5
except (ValueError, AssertionError):
    config.parser.error("analytic_size must be an integer greater/equal to 5")


import MetaAnalytic
import analytic_code
import analytic_dimension
import analytic_structure
