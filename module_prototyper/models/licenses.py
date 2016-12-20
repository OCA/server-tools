# -*- coding: utf-8 -*-
# #############################################################################
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
##############################################################################

BASE_GPL = """
This program is free software: you can redistribute it and/or modify
it under the terms of the {name} as
published by the Free Software Foundation{version}.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the {name}
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


GPL3 = "GPL-3"
GPL3_L = "GPL-3 or any later version"
LGPL3 = "LGPL-3"
LGPL3_L = "LGPL-3 or any later version"
AGPL3 = "AGPL-3"
AGPL3_L = "AGPL-3 or any later version"
OSI = "Other OSI approved license"

V3 = " version 3"
V3L = """, either version 3 of the
License, or (at your option) any later version"""

GPL_LICENSES = {
    GPL3: ("GNU General Public License", V3),
    GPL3_L: ("GNU General Public License", V3L),
    LGPL3: ("GNU Lesser General Public License", V3),
    LGPL3_L: ("GNU Lesser General Public License", V3L),
    AGPL3: ("GNU Affero General Public License", V3),
    AGPL3_L: ("GNU Affero General Public License", V3L),
}

BASE_OSI = """
This program is free software: you should have received a copy of the
license under which it is distributed along with the program.
"""


def get_license_text(license):
    """ Get the python license header for a license """
    if license in GPL_LICENSES:
        name, version = GPL_LICENSES[license]
        return BASE_GPL.format(name=name, version=version).splitlines()
    elif license == OSI:
        return BASE_OSI.splitlines()
    else:
        return ""
