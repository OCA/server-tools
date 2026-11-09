- Tell LDAP logins apart from local password logins.
- Tell trusted device logins apart from authenticator app codes.
- Carry the authentication method of the user who enqueued a queue job into
  the job execution.
- Detect websocket (bus) requests, currently recorded as *Server side*.
- Add bridge modules for non-default authentication methods, such as
  `auth_api_key`, `auth_saml` or `auth_admin_passkey`.
- Odoo 18.0: add the `bearer` route authentication and passkeys
  (`auth_passkey`).
