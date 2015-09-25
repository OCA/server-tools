[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/149/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-server-tools-149)
[![Build Status](https://travis-ci.org/OCA/server-tools.svg?branch=8.0)](https://travis-ci.org/OCA/server-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/server-tools/badge.png?branch=8.0)](https://coveralls.io/r/OCA/server-tools?branch=8.0)
[![Code Climate](https://codeclimate.com/github/OCA/server-tools/badges/gpa.svg)](https://codeclimate.com/github/OCA/server-tools)

Server Environment And Tools
============================

This project aim to deal with modules related to manage Odoo server environment and provide useful tools. You'll find modules that:

 - Manage configuration depending on environment (devs, test, prod,..)
 - Keep the security on update
 - Manage email settings

[//]: # (addons)
Available addons
----------------
addon | version | summary
--- | --- | ---
[admin_technical_features](admin_technical_features/) | 0.1 | Checks the technical features box for admin user.
[auditlog](auditlog/) | 1.0 | Audit Log
[auth_admin_passkey](auth_admin_passkey/) | 2.1.1 | Authentification - Admin Passkey
[auth_dynamic_groups](auth_dynamic_groups/) | 1.0 | Have membership conditions for certain groups
[auth_from_http_remote_user](auth_from_http_remote_user/) | 1.0 | Authenticate via HTTP Remote User
[base_concurrency](base_concurrency/) | 1.0 | Base Concurrency
[base_external_dbsource](base_external_dbsource/) | 1.3 | External Database Sources
[base_field_serialized](base_field_serialized/) | 1.0 | Serialized fields
[base_optional_quick_create](base_optional_quick_create/) | 0.1 | Avoid 'quick create' on m2o fields, on a 'by model' basis
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 1.0 | Report qweb auto generation
[base_suspend_security](base_suspend_security/) | 1.0 | Suspend security checks for a call
[base_user_gravatar](base_user_gravatar/) | 8.0.1.0.0 | Synchronize Gravatar image
[cron_run_manually](cron_run_manually/) | 1.0 | Call cron jobs from their form view
[database_cleanup](database_cleanup/) | 0.1 | Database cleanup
[dbfilter_from_header](dbfilter_from_header/) | 1.0 | dbfilter_from_header
[disable_openerp_online](disable_openerp_online/) | 1.1 | Remove odoo.com bindings
[fetchmail_attach_from_folder](fetchmail_attach_from_folder/) | 1.0 | Attach mails in an IMAP folder to existing objects
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 1.0 | If fetching mails gives error, send an email to sender
[inactive_session_timeout](inactive_session_timeout/) | 1.0 | This module disable all inactive sessions since a given delay
[language_path_mixin](language_path_mixin/) | 1.0 | Setting the partner's language in RML reports
[mail_environment](mail_environment/) | 0.1 | Server env config for mail + fetchmail
[mass_editing](mass_editing/) | 1.3 | Mass Editing
[qweb_usertime](qweb_usertime/) | 1.0 | Add user time rendering support in QWeb
[scheduler_error_mailer](scheduler_error_mailer/) | 1.0 | Send an e-mail when a scheduler fails
[server_environment](server_environment/) | 1.1 | server configuration environment files
[server_environment_files_sample](server_environment_files_sample/) | 1.0 | Example server configuration environment files repository module
[shell](shell/) | 1.0 | Backport of the v9 shell CLI command.
[super_calendar](super_calendar/) | 0.2 | This module allows to create configurable calendars.
[users_ldap_groups](users_ldap_groups/) | 1.2 | Adds user accounts to groups based on rules defined by the administrator.
[users_ldap_mail](users_ldap_mail/) | 1.0 | LDAP mapping for user name and e-mail
[users_ldap_populate](users_ldap_populate/) | 1.2 | LDAP Populate
[web_context_tunnel](web_context_tunnel/) | 2.0 | Web Context Tunnel

Unported addons
---------------
addon | version | summary
--- | --- | ---
[auth_from_http_basic](__unported__/auth_from_http_basic/) | 1.0 (unported) | Authenticate via HTTP basic authentication
[auth_from_http_basic_logout](__unported__/auth_from_http_basic_logout/) | 1.0 (unported) | Authenticate via HTTP basic authentication (logout helper)
[configuration_helper](__unported__/configuration_helper/) | 0.8 (unported) | Configuration Helper
[email_template_template](__unported__/email_template_template/) | 1.0 (unported) | Templates for email templates
[ir_config_parameter_viewer](__unported__/ir_config_parameter_viewer/) | 0.1 (unported) | Ir.config_parameter view
[security_protector](__unported__/security_protector/) | 0.1 (unported) | Security protector
[server_env_base_external_referentials](__unported__/server_env_base_external_referentials/) | 1.0 (unported) | Server environment for base_external_referential
[import_odbc](import_odbc/) | 1.3 (unported) | Import data from SQL and ODBC data sources.

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-server-tools-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-server-tools-8-0)
