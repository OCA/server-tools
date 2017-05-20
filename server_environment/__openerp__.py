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

{
    "name": "server configuration environment files",
    "version": "7.0.1.0.0",
    "depends": ["base", "server_environment_files"],
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "description": """\
Environment file pattern for OpenERP
====================================

This module provides a classical configuration by environnement file
pattern into OpenERP.  Based on code written by WinGo and Camptocamp.

This module allows you to use the classical environment file pattern
by reading a directive call `running_env` in the OpenERP configuration
file::

    [options]
    running_env=dev / prod / etc.

We intended to add a server command line but there is no correct way
to do it.

This method allows you to keep your settings into a module instead of
using config files that might be mixed with openerprc or altered.  It
is an alternative way to the base config file for such configuration
needs .  All your configurations will be read only and accessible
under the admin menu.  If you are not in the 'dev' environment you
will not be able to see the values contained in keys named 'passw'.

At the current time, the module does not allow to set low level
attributes such as database server, etc. .

The first goal of the module is to ensure that OpenERP will never mess
up the external system.  Once installed, profile is mandatory. We do
not want to launch an instance in the dev environment on a production
server.

The configuration files are stored in the `server_environment_files`
module, and user config parser module syntax.  Look at the module to
get some examples.  The `default` configuration are stored in the
`default/` directory. You can add one directory for each environment
you want to define, named after the environment. All config defined in
non-default environments will override or complement the default
config. If your attibutes contain `passw`, it will only be shown in
the `dev` environment.

Example usage
-------------

::

    from server_environment import serv_config
    for key, value in serv_config.items('external_service.ftp'):
       print (key, value)

    serv_config.get('external_service.ftp', 'tls')
    """,
    "website": "http://www.camptocamp.com",
    "category": "Tools",
    "data": [
        'serv_config.xml',
    ],
    "installable": True,
    "active": False,
    "license": 'AGPL',
}
