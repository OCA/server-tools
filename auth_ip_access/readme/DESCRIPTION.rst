This module allows you to restrict who is allowed to login to Odoo based on
the remote IP address. The restriction is applied upon login, and on RPC
calls. Note: valid web sessions are not impacted, and access to the public
website can not be restricted using this module.

When a login is rejected because of a missing IP access rule, a warning is
logged in the application log but no specific information is provided to the
user that is trying to log on. Instead, a generic access denied error is
generated (which is rendered in the web client as 'Wrong login/password'.
