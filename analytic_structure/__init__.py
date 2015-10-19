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
errors = ["[analytic]"]
try:
    assert int(config.get_misc('analytic', 'analytic_size', 5)) >= 5
except (ValueError, AssertionError):
    errors.append("analytic_size must be an integer greater/equal to 5.")
try:
    assert config.get_misc('analytic', 'translate', False) in [True, False]
except AssertionError:
    errors.append("translate must be a boolean value.")
if len(errors) > 1:
    config.parser.error("\n * ".join(errors))

from . import MetaAnalytic   # noqa
from . import analytic_code   # noqa
from . import analytic_dimension   # noqa
from . import analytic_structure   # noqa
