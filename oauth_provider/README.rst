.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

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
  - Any other model information request (depending on the scopes) : http://odoo.example.com/oauth2/data
     Parameters : access_token and model

For example, to configure the *auth_oauth* Odoo module as a client, you will enter these values :

- Provider name : Anything you want
- Client ID : The identifier of the client configured in your Odoo Provider instance
- Body : Text displayed on Odoo's login page link
- Authentication URL : http://odoo.example.com/oauth2/authorize
- Scope : A space separated list of scope codes allowed to the client in your Odoo Provider instance
- Validation URL : http://odoo.example.com/oauth2/tokeninfo
- Data URL : http://odoo.example.com/oauth2/userinfo

Following is an example of obtaining an OAuth2 token in Python using the Legacy Application type (requires `requests_oauth`):

.. code-block:: python

   import os
   import requests

   from oauthlib.oauth2 import LegacyApplicationClient
   from requests_oauthlib import OAuth2Session

   # Allows for no HTTPS verification. DO NOT USE IN PRODUCTION!
   os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

   client_id = '2ec860db-ce81-49c2-b4b7-c71bcbee481f'
   client_secret = 'Test'
   username = 'admin'
   password = 'admin'

   oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
   token = oauth.fetch_token(
       token_url='http://localhost:8060/oauth2/token',
       username=username,
       password=password,
       client_id=client_id,
       client_secret=client_secret,
       scope=['public-pricelist', 'pricelist-item', 'medical-medicament'],
   )

REST API
========

This module also includes a basic REST-style CRUD interface backed by OAuth2 authentication.

List
----

Return allowed information from all records, with optional query.

Route: `/api/rest/1.0/<string:model>`

Accepts: `GET`

Args:
   access_token (str): OAuth2 access token to utilize for the
       operation.
   model (str): Name of model to operate on.
   domain (array, optional): Domain to apply to the search, in the
       standard Odoo format. This will be appended to the scope's
       pre-existing filter.

Returns:
   array of objs: List of data mappings matching query.

Example:

Bash:

.. code-block:: bash

   curl -H "Content-Type: application/json" \
      -H "Authorization: ${ACCESS_TOKEN} \
      -X GET \
      http://localhost:8060/api/gogo/1.0/res.partner?access_token=2J391BkHipPmM9nXv2BF6V07fehWtM&domain=%5B%5B%22company_id%22%2C%20%22%3D%22%2C%201%5D%5D

   {"jsonrpc": "2.0", "id": 5602, "result": [{"name": "Test Partner", "id": 5602}]}

Python:

.. code-block:: python

   json_data = {
       'access_token': token['access_token'],
       'domain': [('company_id', '=', 1)],
   }
   response = requests.get(
       'http://localhost:8060/api/gogo/1.0/res.partner/',
       params=json_data,
   )
   response_data = response.json()

   {u'jsonrpc': u'2.0', u'id': 5602, u'result': [{u'name': u'Test Partner', u'id': 5602}]}

Read
----

Return allowed information from specific records.

Route: `/api/rest/1.0/<string:model>/<int:record_id>`

Accepts: `GET`

Args:
   access_token (str): OAuth2 access token to utilize for the
       operation.
   model (str): Name of model to operate on.
   record_id (int): ID of record to get.

Returns:
   obj: Record data.

Example:

Bash:

.. code-block:: bash

   curl -H "Content-Type: application/json" \
      -H "Authorization: ${ACCESS_TOKEN} \
      -X GET \
      http://localhost:8060/api/gogo/1.0/res.partner/5602?access_token=2J391BkHipPmM9nXv2BF6V07fehWtM

   {"jsonrpc": "2.0", "id": 5602, "result": [{"name": "Test Partner", "id": 5602}]}

Python:

.. code-block:: python

   json_data = {
       'access_token': token['access_token'],
   }
   response = requests.post(
       'http://localhost:8060/api/gogo/1.0/res.partner/5602',
      params=json_data,
   )
   response_data = response.json()

   {u'jsonrpc': u'2.0', u'id': 5602, u'result': [{u'name': u'Test Partner', u'id': 5602}]}

Create
------

Return allowed information from specific records.

Route: `/api/rest/1.0/<string:model>`

Accepts: `POST`

Args:
   access_token (str): OAuth2 access token to utilize for the
       operation.
   model (str): Name of model to operate on.
   kwargs (mixed): All other named arguments are used as the data
       for record mutation.

Returns:
   obj: Record data.

Example:

Bash:

.. code-block:: bash

   curl -H "Content-Type: application/json" \
      -H "Authorization: ${ACCESS_TOKEN} \
      -X POST \
      -d '{ "params": { "access_token": "2J391BkHipPmM9nXv2BF6V07fehWtM", "name": "Test Partner" }' \
      http://localhost:8060/api/gogo/1.0/res.partner

   {"jsonrpc": "2.0", "id": 5602, "result": [{"name": "Test Partner", "id": 5602}]}

Python:

.. code-block:: python

   json_data = {
       'access_token': token['access_token'],
       'name': 'Test Partner',
   }
   response = requests.post(
       'http://localhost:8060/api/gogo/1.0/res.partner',
       json={'params': json_data}
   )
   response_data = response.json()

   {u'jsonrpc': u'2.0', u'id': 5602, u'result': [{u'name': u'Test Partner', u'id': 5602}]}

Update
------

Modify the defined records and return the newly modified data.

Route:
 * `/api/rest/1.0/<string:model>/<int:record_id>`
 * `/api/rest/1.0/<string:model>`

Accepts: `PUT`

Args:
   access_token (str): OAuth2 access token to utilize for the
       operation.
   model (str): Name of model to operate on.
   record_id (int): ID of record to mutate (provided as route argument).
   record_ids (array of ints): IDs of record to mutate (provided as PUT
      argument).
   kwargs (mixed): All other named arguments are used as the data
      for record mutation.

Returns:
   list of objs: Newly modified record data.

Example:

Bash:

.. code-block:: bash

   curl -H "Content-Type: application/json" \
      -H "Authorization: ${ACCESS_TOKEN} \
      -X PUT \
      -d '{ "params": { "access_token": "2J391BkHipPmM9nXv2BF6V07fehWtM", "name": "Test Partner (Edited)" }' \
      http://localhost:8060/api/gogo/1.0/res.partner/5602

   {"jsonrpc": "2.0", "id": 5602, "result": [{"name": "Test Partner (Edited)", "id": 5602}]}

Python

.. code-block:: python

   json_data = {
       'access_token': token['access_token'],
       'name': 'Test Partner (Edited)',
   }
   response = requests.put(
       'http://localhost:8060/api/gogo/1.0/res.partner/5602',
       json={'params': json_data}
   )
   response_data = response.json()

   {u'jsonrpc': u'2.0', u'id': 5602, u'result': [{u'name': u'Test Partner (Edited)', u'id': 5602}]}

Delete
------

Delete the defined records.

Route:
 * `/api/rest/1.0/<string:model>/<int:record_id>`
 * `/api/rest/1.0/<string:model>`

Accepts: `DELETE`

Args:
   access_token (str): OAuth2 access token to utilize for the
       operation.
   model (str): Name of model to operate on.
   record_id (int): ID of record to mutate (provided as route argument).
   record_ids (array of ints): IDs of record to mutate (provided as PUT
      argument).

Returns:
   bool

Example:

Bash:

.. code-block:: bash

   curl -H "Content-Type: application/json" \
      -H "Authorization: ${ACCESS_TOKEN} \
      -X DELETE \
      -d '{ "params": { "access_token": "2J391BkHipPmM9nXv2BF6V07fehWtM" }' \
      http://localhost:8060/api/gogo/1.0/res.partner/5602

   {"jsonrpc": "2.0", "id": null, "result": true}

Python:

.. code-block:: python

   json_data = {
       'access_token': token['access_token'],
   }
   response = requests.delete(
       'http://localhost:8060/api/gogo/1.0/res.partner/5602',
       json={'params': json_data}
   )
   response_data = response.json()

   {u'jsonrpc': u'2.0', u'id': None, u'result': True}


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
