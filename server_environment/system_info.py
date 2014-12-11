# -*- coding: utf-8 -*-
##############################################################################
#
#    Adapted by Nicolas Bessi. Copyright Camptocamp SA
#    Based on Florent Xicluna original code. Copyright Wingo SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import locale
import os
import platform
import subprocess

from openerp import release
from openerp.tools.config import config


def _get_output(cmd):
    bindir = config['root_path']
    p = subprocess.Popen(cmd, shell=True, cwd=bindir, stdout=subprocess.PIPE)
    return p.communicate()[0].rstrip()


def get_server_environment():
    # inspired by server/bin/service/web_services.py
    try:
        rev_id = 'git:%s' % _get_output('git rev-parse HEAD')
    except Exception:
        try:
            rev_id = 'bzr: %s' % _get_output('bzr revision-info')
        except Exception:
            rev_id = 'Can not retrive revison from git or bzr'

    os_lang = '.'.join([x for x in locale.getdefaultlocale() if x])
    if not os_lang:
        os_lang = 'NOT SET'
    if os.name == 'posix' and platform.system() == 'Linux':
        lsbinfo = _get_output('lsb_release -a')
    else:
        lsbinfo = 'not lsb compliant'
    return (
        ('platform', platform.platform()),
        ('os.name', os.name),
        ('lsb_release', lsbinfo),
        ('release', platform.release()),
        ('version', platform.version()),
        ('architecture', platform.architecture()[0]),
        ('locale', os_lang),
        ('python', platform.python_version()),
        ('openerp', release.version),
        ('revision', rev_id),
    )
