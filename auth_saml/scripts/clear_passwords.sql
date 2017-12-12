-- When migrating to a version of "auth_saml" > 2.0, a constraint (optional) has been added to
-- ensure no Odoo user posesses both an SAML user ID and an Odoo password.
-- Run this script to clear passwords of Odoo users that already have an SAML user ID.

UPDATE res_users SET password = NULL WHERE password IS NOT NULL AND saml_uid IS NOT NULL;
