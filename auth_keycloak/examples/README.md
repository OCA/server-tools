# Keycloak dev and test

In this folder you find some examples on how to test your Keycloak auth.

**DISCLAIMER:** this is NOT a guide to help you set up your KC instance.

You must refer to [official docs|https://www.keycloak.org/docs].

None of the settings or the scripts here are meant to work with your setup.

If they do not work, feel free to modify them according to your needs
to be able to test your configuration easily.


## Setup Keycloak

If you want to test on a dev instance and not on the customer's one
start from point 0 and 1. Otherwise, jump to point 2.

0. create a DB and a user:

    ```
    odoodb=# create user keycloak with password 'keycloak';
    CREATE ROLE
    odoodb=# create database keycloak OWNER keycloak;
    CREATE DATABASE
    ```

1. if you don't have a keycloak container already, see keycloak-compose.yml as an example).

2. go to http://localhost:8080 (adapt URL to your setup) and log in as admin (admin/admin)

3. go to "Clients" and click on "create" button

4. create 'Odoo' client (you can import `odoo-client.json` to test)

5. configure KC client properly. In particular, see that these flags are turned on:

   ```json
    "consentRequired": false,
    "standardFlowEnabled": true,
    "implicitFlowEnabled": true,
    "directAccessGrantsEnabled": true,
   ```

   And make sure your redirect URI matches with your odoo instance.

   (Note that these settings might differ from your final configuration
   but they are required for the scripts and our current internal configuration to work.)

6. go to "Manage / Users" and create a new user (default `c2c`)

7. switch to "Credentials" tab, uncheck "temporary" flag and set a new pwd (default `c2c`)

8. edit `/etc/hosts` and add a line `127.0.0.1 keycloak`

Now your dev instance is ready to be tested.


**NOTE:** if the user already exists in Odoo,
it's keycloak's ID ("sub") should be added manually in the Oauth ID field in Odoo.
This is because it's automatically stored only on new signups.

**WARNING:** if you have an LDAP configuration which is not working locally
go to company settings and delete it otherwise the auth will hang forever.


## Test calls

You can use these scripts on real or dev/test keycloak instances
to test if they are properly configured to work smoothly w/ Odoo.

Indeed, what they do, is to simulate Odoo calls.


### Requirements

```
cd path/to/auth_keycloak/examples
pip install -r requirements.txt
```

### Init

1st of all you need a token. Run:

```
python get_token.py
```

If everything goes fine, you'll see something like:

```
$ python examples/get_token.py
Username [admin]:
Password [admin]:
Client ID [odoo]:
Client secret [6991c9e8-88bb-4cd8-bc94-7ffd914b0167]:
Calling http://localhost:8080/auth/realms/Odoo/protocol/openid-connect/token
Access token:
eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5cDhwS29xVHVKUElGa1ZTMVdGWGxQZlpOdzRWZ042eXpocGFOZFBjWmQwIn0.eyJqdGkiOiIzMWVjODZiYS00OTcwLTRhNjEtODEyZi0xYTI2ZGYyOGY3OTIiLCJleHAiOjE1MjYzMDU3NzYsIm5iZiI6MCwiaWF0IjoxNTI2MzA1NDc2LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvYXV0aC9yZWFsbXMvT2RvbyIsImF1ZCI6Im9kb28iLCJzdWIiOiIyYmE1ZmQ0Ni00ZTNhLTRjYWYtOTNlNy0wODcwNDcyMGE5MzYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJvZG9vIiwiYXV0aF90aW1lIjowLCJzZXNzaW9uX3N0YXRlIjoiNGQwZTM5MzgtOTRjNi00NmY4LWFlN2QtZjIwZjA5YjU2YjhjIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyJodHRwOi8vb2Rvbzo4MDY5Il0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7Im9kb28iOnsicm9sZXMiOlsidGVzdCJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYzJjIn0.Ll5ZG6FdlQA_mlalixT8UFrhcgP3yx_qC-u-hl9TqnksrbN7x1ZOqy7_awkV5i_6TPlAKmoq5cHtWM0opJgRMrV7e5ZZ4ZEfEbw7PFSE1SdC7N961vhMx5Gts2l9xy0WQOJoeT3ImVdRgVtK8mIOYmBpiZXUJY7KfDTVUXt6HT9AVmNYArxBI1PZlbIRxwb_rSXMs1KAll3lcs506t5CSb2Utjvsx1kEcf5ZMfKiXkz0xAyT1ZMnWjpUu_iHKQQWLcefDvCDqmSofgR6WJ1hD9kJKsrY8BLn-BvLVsSzgj8jK8El6zXu0_rBscjyVaM4j-JeQ0qUqfe7Stzw8kbIUw
Saved to /tmp/keycloak.json
```
Meaningful data as well as our brand new token are stored into "/tmp/keycloak.json".

If want you can pass custom arguments when prompted.

If you get an error, check Keycloak's logs.

**NOTE:** by default we call `localhost` but you can pass extra arguments for domain and real like this:

```
$ python get_token.py --domain=https://keycloak.mycompany.io --realm=mycompany
[...]
Calling https://keycloak.mycompany.io/auth/realms/mycompany/protocol/openid-connect/token

```

### Token validation

Run:

```
python cli.py validate_token
```
If everything goes fine, you'll see something like:
```
$ python examples/cli.py validate_token
Calling http://localhost:8080/auth/realms/Odoo/protocol/openid-connect/token/introspect
{u'username': u'c2c', u'active': True, u'session_state': u'4d0e3938-94c6-46f8-ae7d-f20f09b56b8c', u'aud': u'odoo', u'realm_access': {u'roles': [u'uma_authorization']}, u'iss': u'http://localhost:8080/auth/realms/Odoo', u'resource_access': {u'account': {u'roles': [u'manage-account', u'manage-account-links', u'view-profile']}, u'odoo': {u'roles': [u'test']}}, u'allowed-origins': [u'http://odoo:8069'], u'preferred_username': u'c2c', u'acr': u'1', u'client_id': u'odoo', u'jti': u'31ec86ba-4970-4a61-812f-1a26df28f792', u'exp': 1526305776, u'auth_time': 0, u'azp': u'odoo', u'iat': 1526305476, u'typ': u'Bearer', u'nbf': 0, u'sub': u'2ba5fd46-4e3a-4caf-93e7-08704720a936'}
```
If the token is expired meanwhile you'll see another call to `get_token`.

If you get an error, check Keycloak's logs.


### User introspection

Run:

```
python cli.py user_info
```
If everything goes fine, you'll see something like:
```
$ python examples/cli.py user_info
Calling http://localhost:8080/auth/realms/Odoo/protocol/openid-connect/userinfo
User info:
{u'preferred_username': u'c2c', u'sub': u'2ba5fd46-4e3a-4caf-93e7-08704720a936'}
```
If you get an error, check Keycloak's logs.


### User creation

Run:

```
$ python cli.py create_user --username=myuser  --values=a:1;b:2
```

If everything goes fine, you'll see something like:

```
$ python cli.py create_user --username=metesting --values=email:me@testing.com
Calling http://localhost:8080/auth/admin/realms/master/users
User created.
```

If you get an error, you'll see something like

```
$ python cli.py create_user --username=metest1 --values=email:me@test1.com
Calling http://localhost:8080/auth/admin/realms/master/users
Something went wrong. Quitting. 
Status: 409
Reason: Conflict
Result: {"errorMessage":"User exists with same username"}
```

### User search

Run:

```
$ python cli.py search_users
```

If everything goes fine, you'll see something like:

```
$ python cli.py search_users
Calling http://localhost:8080/auth/admin/realms/master/users
User info:
[{u'username': u'pippo', u'access': {...}}, {u'username': u'johndoe', u'access': {...}}, ]
```

You can filter by user values (see KC docs) by passing `--search`:

```
$ python cli.py search_users --search=pluto
Calling http://localhost:8080/auth/admin/realms/master/users?search=pluto
User info:
[{u'username': u'pippo', u'access': {u'manage': True, u'manageGroupMembership': True, u'impersonate': True, u'mapRoles': True, u'view': True}, u'firstName': u'Pippo', u'notBefore': 0, u'emailVerified': False, u'requiredActions': [], u'enabled': True, u'email': u'pippo@pluto.com', u'createdTimestamp': 1539871348882, u'totp': False, u'disableableCredentialTypes': [], u'lastName': u'Pluto', u'id': u'1feb89e6-76bd-44a1-ab5d-df28b6477e19'}, {u'username': u'pluto', u'access': {u'manage': True, u'manageGroupMembership': True, u'impersonate': True, u'mapRoles': True, u'view': True}, u'notBefore': 0, u'emailVerified': True, u'enabled': True, u'email': u'pluto@test.com', u'createdTimestamp': 1540306774544, u'totp': False, u'disableableCredentialTypes': [], u'requiredActions': [], u'id': u'e06e1f36-7303-40b5-9a2e-a392ae1ec728'}]
```

If you get an error, check logs.
