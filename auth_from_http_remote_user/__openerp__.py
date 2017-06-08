# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Laurent Mignon
#    Copyright 2014 'ACSONE SA/NV'
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
{
    'name': 'Authenticate via HTTP Remote User',
    'version': '1.0',
    'category': 'Tools',
    'description': """
Allow users to be automatically logged in.
==========================================

This module initialize the session by looking for the field HTTP_REMOTE_USER in
the HEADER of the HTTP request and trying to bind the given value to a user
This module must be loaded at startup; Add the *--load* parameter to the startup
command: ::

  --load=web,web_kanban,auth_from_http_remote_user, ...

If the field is not found or no user matches the given one, it can lets the
system redirect to the login page (default) or issue a login error page depending
of the configuration.

How to test the module with Apache [#]_
----------------------------------------

Apache can be used as a reverse proxy providing the authentication and adding the
required field in the Http headers.

Install apache:  ::

   $ sudo apt-get install apache2


Define a new vhost to Apache by putting a new file in /etc/apache2/sites-available: ::

   $ sudo vi  /etc/apache2/sites-available/MY_VHOST.com

with the following content: ::

   <VirtualHost *:80>
     ServerName MY_VHOST.com
     ProxyRequests Off
     <Location />
       AuthType Basic
       AuthName "Test OpenErp auth_from_http_remote_user"
       AuthBasicProvider file
       AuthUserFile /etc/apache2/MY_VHOST.htpasswd
       Require valid-user

       RewriteEngine On
       RewriteCond %{LA-U:REMOTE_USER} (.+)
       RewriteRule . - [E=RU:%1]
       RequestHeader set Remote-User "%{RU}e" env=RU
     </Location>

     ProxyPass / http://127.0.0.1:8069/  retry=10
     ProxyPassReverse  / http://127.0.0.1:8069/
     ProxyPreserveHost On
   </VirtualHost>

.. important:: The *RequestHeader* directive is used to add the *Remote-User* field
   in the http headers. By default an *'Http-'* prefix is added to the field name.
   In OpenErp, header's fields name are normalized. As result of this normalization,
   the 'Http-Remote-User' is available as 'HTTP_REMOTE_USER'. If you don't know how
   your specified field is seen by OpenErp, run your server in debug mode once the
   module is activated and look for an entry like: ::

     DEBUG openerp1 openerp.addons.auth_from_http_remote_user.controllers.session:
     Field 'HTTP_MY_REMOTE_USER' not found in http headers
     {'HTTP_AUTHORIZATION': 'Basic YWRtaW46YWRtaW4=', ..., 'HTTP_REMOTE_USER': 'demo')

Enable the required apache modules: ::

   $ sudo a2enmod headers
   $ sudo a2enmod proxy
   $ sudo a2enmod rewrite
   $ sudo a2enmod proxy_http

Enable your new vhost: ::

  $ sudo a2ensite MY_VHOST.com

Create the *htpassword* file used by the configured basic authentication: ::

   $ sudo htpasswd -cb /etc/apache2/MY_VHOST.htpasswd admin admin
   $ sudo htpasswd -b /etc/apache2/MY_VHOST.htpasswd demo demo

For local test, add the *MY_VHOST.com* in your /etc/vhosts file.

Finally reload the configuration: ::

   $ sudo service apache2 reload

Open your browser and go to MY_VHOST.com. If everything is well configured, you are prompted
for a login and password outside OpenErp and are automatically logged in the system.

.. [#] Based on a ubuntu 12.04 env

""",
    'author': 'Acsone SA/NV',
    'maintainer': 'ACSONE SA/NV',
    'website': 'http://www.acsone.eu',
    'depends': ['web'],
    "license": "AGPL-3",
    "js": ['static/src/js/auth_from_http_remote_user.js'],
    'data': [
        'res_config_view.xml',
        'res_config_data.xml'],
    "demo": [],
    "test": [],
    "active": False,
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "application": False,
}
