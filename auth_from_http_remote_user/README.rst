.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================================
Allow users to be automatically logged in
=========================================

This module initialize the session by looking for the field HTTP_REMOTE_USER in
the HEADER of the HTTP request and trying to bind the given value to a user.
To be active, the module must be installed in the expected databases and loaded
at startup; Add the *--load* parameter to the startup command: ::

  --load=web,web_kanban,auth_from_http_remote_user, ...

If the field is found in the header and no user matches the given one, the
system issue a login error page. (*401* `Unauthorized`)

Use case.
=========

The module allows integration with external security systems [#]_ that can pass
along authentication of a user via Remote_User HTTP header field. In many
cases, this is achieved via server like Apache HTTPD or nginx proxying Odoo.

.. important:: When proxying your Odoo server with Apache or nginx, It's
   important to filter out the Remote_User HTTP header field before your
   request is processed by the proxy to avoid security issues. In apache you
   can do it by using the RequestHeader directive in your VirtualHost
   section  ::

    <VirtualHost *:80>
     ServerName MY_VHOST.com
     ProxyRequests Off
    ...

     RequestHeader unset Remote-User early
     ProxyPass / http://127.0.0.1:8069/  retry=10
     ProxyPassReverse  / http://127.0.0.1:8069/
     ProxyPreserveHost On
    </VirtualHost>


How to test the module with Apache [#]_
=======================================

Apache can be used as a reverse proxy providing the authentication and adding
the required field in the Http headers.

Install apache:  ::

   $ sudo apt-get install apache2


Define a new vhost to Apache by putting a new file in
/etc/apache2/sites-available: ::

   $ sudo vi  /etc/apache2/sites-available/MY_VHOST.com

with the following content: ::

   <VirtualHost *:80>
     ServerName MY_VHOST.com
     ProxyRequests Off
     <Location />
       AuthType Basic
       AuthName "Test Odoo auth_from_http_remote_user"
       AuthBasicProvider file
       AuthUserFile /etc/apache2/MY_VHOST.htpasswd
       Require valid-user

       RewriteEngine On
       RewriteCond %{LA-U:REMOTE_USER} (.+)
       RewriteRule . - [E=RU:%1]
       RequestHeader set Remote-User "%{RU}e" env=RU
     </Location>

     RequestHeader unset Remote-User early
     ProxyPass / http://127.0.0.1:8069/  retry=10
     ProxyPassReverse  / http://127.0.0.1:8069/
     ProxyPreserveHost On
   </VirtualHost>

.. important:: The *RequestHeader* directive is used to add the *Remote-User*
   field in the http headers. By default an *'Http-'* prefix is added to the
   field name.
   In Odoo, header's fields name are normalized. As result of this
   normalization, the 'Http-Remote-User' is available as 'HTTP_REMOTE_USER'.
   If you don't know how your specified field is seen by Odoo, run your
   server in debug mode once the module is activated and look for an entry
   like: ::

     DEBUG openerp1 openerp.addons.auth_from_http_remote_user.controllers.
     session:
     Field 'HTTP_MY_REMOTE_USER' not found in http headers
     {'HTTP_AUTHORIZATION': 'Basic YWRtaW46YWRtaW4=', ...,
     'HTTP_REMOTE_USER': 'demo')

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

Open your browser and go to MY_VHOST.com. If everything is well configured, you
are prompted for a login and password outside Odoo and are automatically
logged in the system.

.. [#] Shibolleth, Tivoli access manager, ..
.. [#] Based on a ubuntu 12.04 env

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Laurent Mignon <laurent.mignon@acsone.eu>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
