.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
OAuth Provider
==============

This module allows you to turn Odoo into an OAuth 2 provider.

It's meant to provide the basic authentication feature, and some data access routes.
But you are encouraged to create custom routes, in other modules, to give structured data for any specific need.

Installation
============

To install this module, you need to:

#. Install the oauthlib python module
#. Install the module like any other in Odoo
#. For the token retrieval to work on a multi-database instance, you should add this module in the server_wide_modules list

Configuration
=============

This module requires you to configure two things :

#. The scopes are used to define restricted data access
#. The clients are used to declare applications that will be allowed to request tokens and data

To configure scopes, you need to:

#. Go to Settings > Users > OAuth Provider Scopes
#. Create some scopes:

 - The scope name and description will be displayed to the user on the authorization page.
 - The code is the value provided by the OAuth clients to request access to the scope.
 - The model defines which model the scope is linked to (access to user data, partners, sales orders, etc.).
 - The filter allows you to determine which records will be accessible through this scope. No filter means all records of the model are accessible.
 - The field names allows you to define which fields will be provided to the clients. An empty list only returns the id of accessible records.

To configure clients, you need to:

#. Go to Settings > Users > OAuth Provider Clients
#. Create at least one client:

 - The name will be displayed to the user on the authorization page.
 - The client identifier is the value provided by the OAuth clients to request authorizations/tokens.
 - The application type adapts the process to four pre-defined profiles:

   - Web Application : Authorization Code Grant
   - Mobile Application : Implicit Grant
   - Legacy Application : Resource Owner Password Credentials Grant
   - Backend Application : User Credentials Grant (not implemented yet)

 - The skip authorization checkbox allows the client to skip the authorization page, and directly deliver a token without prompting the user (useful when the application is trusted).
 - The allowed scopes list defines which data will be accessible by this client applicaton.
 - The allowed redirect URIs must match the URI sent by the client, to avoid redirecting users to an unauthorized service. The first value in the list is the default redirect URI.

For example, to configure an Odoo's *auth_oauth* module compatible client, you will enter these values :

- Name : Anything you want
- Client identifier : The identifier you want to give to this client
- Application Type : Mobile Application (Odoo uses the implicit grant mode, which corresponds to the mobile application profile)
- Allowed Scopes : Nothing required, but allowing access to current user's email and name is used by Odoo to fill user's information on signup
- Allowed Redirect URIs : http://odoo.example.com/auth_oauth/signin

Usage
=====

This module will allow OAuth clients to use your Odoo instance as an OAuth provider.

Once configured, you must give these information to your client application :

#. Client identifier : Identifies the application (to be able to check allowed scopes and redirect URIs)
#. Allowed scopes : The codes of scopes allowed for this client
#. URLs for the requests :

  - Authorization request : http://odoo.example.com/oauth2/authorize
  - Token request : http://odoo.example.com/oauth2/token
  - Token information request : http://odoo.example.com/oauth2/tokeninfo
     Parameters : access_token
  - User information request : http://odoo.example.com/oauth2/userinfo
     Parameters : access_token
  - Any other model information request (depending on the scopes) : http://odoo.example.com/oauth2/otherinfo
     Parameters : access_token and model

For example, to configure the *auth_oauth* Odoo module as a client, you will enter these values :

- Provider name : Anything you want
- Client ID : The identifier of the client configured in your Odoo Provider instance
- Body : Text displayed on Odoo's login page link
- Authentication URL : http://odoo.example.com/oauth2/authorize
- Scope : A space separated list of scope codes allowed to the client in your Odoo Provider instance
- Validation URL : http://odoo.example.com/oauth2/tokeninfo
- Data URL : http://odoo.example.com/oauth2/userinfo

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Known issues / Roadmap
======================

* Implement the backend application profile (client credentials grant type)
* Add checkboxes on the authorization page to allow the user to disable some scopes for a token ? (I don't know if this is allowed in the OAuth protocol)

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

* Sylvain Garancher <sylvain.garancher@syleam.fr>
* Dave Lasley <dave@laslabs.com>

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
