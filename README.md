[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/149/9.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-server-tools-149)
[![Build Status](https://travis-ci.org/OCA/server-tools.svg?branch=9.0)](https://travis-ci.org/OCA/server-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/server-tools/badge.png?branch=9.0)](https://coveralls.io/r/OCA/server-tools?branch=9.0)
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
[base_multi_image](base_multi_image/) | 9.0.1.0.0 | Allow multiple images for database objects
[base_suspend_security](base_suspend_security/) | 9.0.1.0.0 | Suspend security checks for a call
[base_technical_features](base_technical_features/) | 9.0.1.0.0 | Access to technical features without activating debug mode
[base_user_gravatar](base_user_gravatar/) | 9.0.1.0.0 | Synchronize Gravatar Image
[date_range](date_range/) | 9.0.1.0.0 | Manage all kind of date range
[dbfilter_from_header](dbfilter_from_header/) | 9.0.1.0.0 | Filter databases with HTTP headers
[disable_odoo_online](disable_odoo_online/) | 9.0.1.0.0 | Remove odoo.com bindings
[mail_environment](mail_environment/) | 9.0.1.0.0 | Configure mail servers with server_environment_files
[server_environment](server_environment/) | 9.0.1.1.0 | move some configurations out of the database
[server_environment_files_sample](server_environment_files_sample/) | 9.0.1.0.0 | sample config file for server_environment
[users_ldap_mail](users_ldap_mail/) | 9.0.1.0.0 | LDAP mapping for user name and e-mail
[users_ldap_populate](users_ldap_populate/) | 9.0.1.0.0 | LDAP Populate

Unported addons
---------------
addon | version | summary
--- | --- | ---
[admin_technical_features](admin_technical_features/) | 8.0.0.1.0 (unported) | Checks the technical features box for admin user.
[auditlog](auditlog/) | 8.0.1.0.0 (unported) | Audit Log
[auth_admin_passkey](auth_admin_passkey/) | 8.0.2.1.1 (unported) | Authentification - Admin Passkey
[auth_dynamic_groups](auth_dynamic_groups/) | 8.0.1.0.0 (unported) | Have membership conditions for certain groups
[auth_from_http_basic](auth_from_http_basic/) | 1.0 (unported) | Authenticate via HTTP basic authentication
[auth_from_http_basic_logout](auth_from_http_basic_logout/) | 1.0 (unported) | Authenticate via HTTP basic authentication (logout helper)
[auth_from_http_remote_user](auth_from_http_remote_user/) | 8.0.1.0.0 (unported) | Authenticate via HTTP Remote User
[base_debug4all](base_debug4all/) | 8.0.1.0.0 (unported) | Shows full debug options for all users
[base_external_dbsource](base_external_dbsource/) | 8.0.1.3.0 (unported) | External Database Sources
[base_optional_quick_create](base_optional_quick_create/) | 8.0.0.1.0 (unported) | Avoid 'quick create' on m2o fields, on a 'by model' basis
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 8.0.1.0.0 (unported) | Report qweb auto generation
[configuration_helper](configuration_helper/) | 0.8 (unported) | Configuration Helper
[database_cleanup](database_cleanup/) | 8.0.0.1.0 (unported) | Database cleanup
[email_template_template](email_template_template/) | 1.0 (unported) | Templates for email templates
[fetchmail_attach_from_folder](fetchmail_attach_from_folder/) | 8.0.1.0.1 (unported) | Attach mails in an IMAP folder to existing objects
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 8.0.1.0.0 (unported) | If fetching mails gives error, send an email to sender
[import_odbc](import_odbc/) | 1.3 (unported) | Import data from SQL and ODBC data sources.
[inactive_session_timeout](inactive_session_timeout/) | 8.0.1.0.0 (unported) | This module disable all inactive sessions since a given delay
[ir_config_parameter_viewer](ir_config_parameter_viewer/) | 0.1 (unported) | Ir.config_parameter view
[language_path_mixin](language_path_mixin/) | 8.0.1.0.0 (unported) | Setting the partner's language in RML reports
[mass_editing](mass_editing/) | 8.0.1.3.0 (unported) | Mass Editing
[module_prototyper](module_prototyper/) | 8.0.0.3.0 (unported) | Prototype your module.
[qweb_usertime](qweb_usertime/) | 8.0.1.0.0 (unported) | Add user time rendering support in QWeb
[scheduler_error_mailer](scheduler_error_mailer/) | 8.0.1.0.0 (unported) | Send an e-mail when a scheduler fails
[security_protector](security_protector/) | 0.1 (unported) | Security protector
[server_env_base_external_referentials](server_env_base_external_referentials/) | 1.0 (unported) | Server environment for base_external_referential
[super_calendar](super_calendar/) | 8.0.0.2.0 (unported) | This module allows to create configurable calendars.
[users_ldap_groups](users_ldap_groups/) | 8.0.1.2.0 (unported) | Adds user accounts to groups based on rules defined by the administrator.
[web_context_tunnel](web_context_tunnel/) | 8.0.2.0.0 (unported) | Web Context Tunnel

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-server-tools-9-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-server-tools-9-0)
