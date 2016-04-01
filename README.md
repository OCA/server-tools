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
[admin_technical_features](admin_technical_features/) | 8.0.0.1.0 | Checks the technical features box for admin user.
[auditlog](auditlog/) | 8.0.1.3.0 | Audit Log
[auth_admin_passkey](auth_admin_passkey/) | 8.0.2.1.1 | Authentification - Admin Passkey
[auth_brute_force](auth_brute_force/) | 8.0.1.0.0 | Tracks Authentication Attempts and Prevents Brute-force Attacks module
[auth_dynamic_groups](auth_dynamic_groups/) | 8.0.1.0.0 | Have membership conditions for certain groups
[auth_from_http_remote_user](auth_from_http_remote_user/) | 8.0.1.0.0 | Authenticate via HTTP Remote User
[auth_signup_verify_email](auth_signup_verify_email/) | 8.0.1.0.0 | Force uninvited users to use a good email for signup
[auth_supplier](auth_supplier/) | 8.0.1.0.0 | Auth Supplier
[base_concurrency](base_concurrency/) | 8.0.1.0.0 | Base Concurrency
[base_custom_info](base_custom_info/) | 8.0.1.0.0 | Add custom field in models
[base_debug4all](base_debug4all/) | 8.0.1.0.0 | Shows full debug options for all users
[base_export_manager](base_export_manager/) | 8.0.1.0.0 | Manages model export profiles
[base_external_dbsource](base_external_dbsource/) | 8.0.1.3.0 | External Database Sources
[base_ir_filters_active](base_ir_filters_active/) | 8.0.1.0.0 | Allows you to disable (hide) filters
[base_module_doc_rst](base_module_doc_rst/) | 8.0.1.0.0 | Modules Technical Guides in RST and Relationship Graphs
[base_multi_image](base_multi_image/) | 8.0.2.0.0 | Allow multiple images for database objects
[base_optional_quick_create](base_optional_quick_create/) | 8.0.0.1.0 | Avoid 'quick create' on m2o fields, on a 'by model' basis
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 8.0.1.0.0 | Report qweb auto generation
[base_suspend_security](base_suspend_security/) | 8.0.1.0.0 | Suspend security checks for a call
[base_user_gravatar](base_user_gravatar/) | 8.0.1.0.0 | Synchronize Gravatar image
[base_user_reset_access](base_user_reset_access/) | 8.0.1.0.0 | Reset User Access Right
[cron_run_manually](cron_run_manually/) | 8.0.1.0.0 | Call cron jobs from their form view
[database_cleanup](database_cleanup/) | 8.0.0.1.0 | Database cleanup
[datetime_formatter](datetime_formatter/) | 8.0.1.0.0 | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 8.0.1.0.1 | dbfilter_from_header
[dead_mans_switch_client](dead_mans_switch_client/) | 8.0.1.0.1 | Be notified when customers' odoo instances go down
[dead_mans_switch_server](dead_mans_switch_server/) | 8.0.1.0.0 | Be notified when customers' odoo instances go down
[disable_openerp_online](disable_openerp_online/) | 8.0.1.1.0 | Remove odoo.com bindings
[fetchmail_attach_from_folder](fetchmail_attach_from_folder/) | 8.0.1.0.1 | Attach mails in an IMAP folder to existing objects
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 8.0.1.0.0 | If fetching mails gives error, send an email to sender
[inactive_session_timeout](inactive_session_timeout/) | 8.0.1.0.0 | This module disable all inactive sessions since a given delay
[language_path_mixin](language_path_mixin/) | 8.0.1.0.0 | Setting the partner's language in RML reports
[log_forwarded_for_ip](log_forwarded_for_ip/) | 8.0.1.0.0 | Displays source IPs in log when behind a reverse proxy
[mail_environment](mail_environment/) | 8.0.0.1.0 | Server env config for mail + fetchmail
[mass_editing](mass_editing/) | 8.0.1.3.0 | Mass Editing
[module_prototyper](module_prototyper/) | 8.0.0.3.0 | Prototype your module.
[qweb_usertime](qweb_usertime/) | 8.0.1.0.0 | Add user time rendering support in QWeb
[save_translation_file](save_translation_file/) | 8.0.1.0.0 | Allows developpers to easily generate i18n files
[scheduler_error_mailer](scheduler_error_mailer/) | 8.0.1.0.0 | Send an e-mail when a scheduler fails
[server_environment](server_environment/) | 8.0.1.1.0 | server configuration environment files
[server_environment_files_sample](server_environment_files_sample/) | 8.0.1.0.0 | Example server configuration environment files repository module
[shell](shell/) | 8.0.1.0.0 | Backport of the v9 shell CLI command.
[super_calendar](super_calendar/) | 8.0.0.2.0 | This module allows to create configurable calendars.
[users_ldap_groups](users_ldap_groups/) | 8.0.1.2.0 | Adds user accounts to groups based on rules defined by the administrator.
[users_ldap_mail](users_ldap_mail/) | 8.0.1.0.0 | LDAP mapping for user name and e-mail
[users_ldap_populate](users_ldap_populate/) | 8.0.1.2.0 | LDAP Populate
[users_ldap_push](users_ldap_push/) | 8.0.1.0.0 | Creates a ldap entry when you create a user in Odoo
[web_context_tunnel](web_context_tunnel/) | 8.0.2.0.0 | Web Context Tunnel

Unported addons
---------------
addon | version | summary
--- | --- | ---
[auth_from_http_basic](auth_from_http_basic/) | 1.0 (unported) | Authenticate via HTTP basic authentication
[auth_from_http_basic_logout](auth_from_http_basic_logout/) | 1.0 (unported) | Authenticate via HTTP basic authentication (logout helper)
[configuration_helper](configuration_helper/) | 0.8 (unported) | Configuration Helper
[email_template_template](email_template_template/) | 1.0 (unported) | Templates for email templates
[import_odbc](import_odbc/) | 1.3 (unported) | Import data from SQL and ODBC data sources.
[ir_config_parameter_viewer](ir_config_parameter_viewer/) | 0.1 (unported) | Ir.config_parameter view
[security_protector](security_protector/) | 0.1 (unported) | Security protector
[server_env_base_external_referentials](server_env_base_external_referentials/) | 1.0 (unported) | Server environment for base_external_referential

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-server-tools-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-server-tools-8-0)
