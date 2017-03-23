[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/149/10.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-server-tools-149)
[![Build Status](https://travis-ci.org/OCA/server-tools.svg?branch=10.0)](https://travis-ci.org/OCA/server-tools)
[![Coverage Status](https://coveralls.io/repos/OCA/server-tools/badge.png?branch=10.0)](https://coveralls.io/r/OCA/server-tools?branch=10.0)
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
[auditlog](auditlog/) | 10.0.1.0.0 | Audit Log
[auth_signup_verify_email](auth_signup_verify_email/) | 10.0.1.0.0 | Force uninvited users to use a good email for signup
[auto_backup](auto_backup/) | 10.0.1.0.2 | Backups database
[base_exception](base_exception/) | 10.0.1.0.0 | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_external_dbsource](base_external_dbsource/) | 10.0.2.0.0 | External Database Sources
[base_external_dbsource_firebird](base_external_dbsource_firebird/) | 10.0.1.0.0 | External Database Source - Firebird
[base_external_dbsource_mssql](base_external_dbsource_mssql/) | 10.0.1.0.0 | External Database Source - MSSQL
[base_external_dbsource_mysql](base_external_dbsource_mysql/) | 10.0.1.0.0 | External Database Source - MySQL
[base_external_dbsource_odbc](base_external_dbsource_odbc/) | 10.0.1.0.0 | External Database Source - ODBC
[base_external_dbsource_oracle](base_external_dbsource_oracle/) | 10.0.1.0.0 | External Database Source - Oracle
[base_external_dbsource_sqlite](base_external_dbsource_sqlite/) | 10.0.1.0.0 | External Database Source - SQLite
[base_kanban_stage](base_kanban_stage/) | 10.0.1.0.0 | Provides stage model and abstract logic for inheritance
[base_kanban_stage_state](base_kanban_stage_state/) | 10.0.1.0.0 | Maps stages from base_kanban_stage to states
[base_multi_image](base_multi_image/) | 10.0.1.0.0 | Allow multiple images for database objects
[base_suspend_security](base_suspend_security/) | 10.0.1.0.0 | Suspend security checks for a call
[base_technical_features](base_technical_features/) | 10.0.1.0.0 | Access to technical features without activating debug mode
[base_user_gravatar](base_user_gravatar/) | 10.0.1.0.0 | Synchronize Gravatar Image
[base_user_role](base_user_role/) | 10.0.1.0.0 | User roles
[date_range](date_range/) | 10.0.1.0.0 | Manage all kind of date range
[dbfilter_from_header](dbfilter_from_header/) | 10.0.1.0.0 | Filter databases with HTTP headers
[disable_odoo_online](disable_odoo_online/) | 10.0.1.0.0 | Remove odoo.com Bindings
[keychain](keychain/) | 10.0.1.0.0 | Store accounts and credentials
[mass_editing](mass_editing/) | 10.0.1.0.0 | Mass Editing
[mass_sorting](mass_sorting/) | 10.0.1.0.0 | Sort any models by any fields list
[module_prototyper](module_prototyper/) | 10.0.1.0.0 | Prototype your module.
[password_security](password_security/) | 10.0.1.0.1 | Allow admin to set password security requirements.
[scheduler_error_mailer](scheduler_error_mailer/) | 10.0.1.0.0 | Scheduler Error Mailer
[users_ldap_mail](users_ldap_mail/) | 10.0.1.0.0 | LDAP mapping for user name and e-mail
[users_ldap_populate](users_ldap_populate/) | 10.0.1.0.0 | LDAP Populate

Unported addons
---------------
addon | version | summary
--- | --- | ---
[admin_technical_features](admin_technical_features/) | 9.0.0.1.0 (unported) | Checks the technical features box for admin user.
[attachment_base_synchronize](attachment_base_synchronize/) | 9.0.1.0.0 (unported) | Attachment Base Synchronize
[auth_admin_passkey](auth_admin_passkey/) | 8.0.2.1.1 (unported) | Authentification - Admin Passkey
[auth_dynamic_groups](auth_dynamic_groups/) | 8.0.1.0.0 (unported) | Have membership conditions for certain groups
[auth_from_http_basic](auth_from_http_basic/) | 1.0 (unported) | Authenticate via HTTP basic authentication
[auth_from_http_basic_logout](auth_from_http_basic_logout/) | 1.0 (unported) | Authenticate via HTTP basic authentication (logout helper)
[auth_from_http_remote_user](auth_from_http_remote_user/) | 8.0.1.0.0 (unported) | Authenticate via HTTP Remote User
[auth_session_timeout](auth_session_timeout/) | 9.0.1.0.0 (unported) | This module disable all inactive sessions since a given delay
[auth_supplier](auth_supplier/) | 9.0.2.0.0 (unported) | Auth Supplier
[base_custom_info](base_custom_info/) | 9.0.1.0.0 (unported) | Add custom field in models
[base_debug4all](base_debug4all/) | 8.0.1.0.0 (unported) | Shows full debug options for all users
[base_export_manager](base_export_manager/) | 9.0.1.1.0 (unported) | Manage model export profiles
[base_optional_quick_create](base_optional_quick_create/) | 9.0.1.0.0 (unported) | Avoid 'quick create' on m2o fields, on a 'by model' basis
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 9.0.1.0.0 (unported) | Report qweb auto generation
[configuration_helper](configuration_helper/) | 9.0.1.0.0 (unported) | Configuration Helper
[database_cleanup](database_cleanup/) | 9.0.1.0.0 (unported) | Database cleanup
[dead_mans_switch_client](dead_mans_switch_client/) | 9.0.1.0.1 (unported) | Be notified when customers' odoo instances go down
[email_template_template](email_template_template/) | 1.0 (unported) | Templates for email templates
[fetchmail_attach_from_folder](fetchmail_attach_from_folder/) | 8.0.1.0.1 (unported) | Attach mails in an IMAP folder to existing objects
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 8.0.1.0.0 (unported) | If fetching mails gives error, send an email to sender
[import_odbc](import_odbc/) | 1.3 (unported) | Import data from SQL and ODBC data sources.
[ir_config_parameter_viewer](ir_config_parameter_viewer/) | 0.1 (unported) | Ir.config_parameter view
[language_path_mixin](language_path_mixin/) | 8.0.1.0.0 (unported) | Setting the partner's language in RML reports
[letsencrypt](letsencrypt/) | 9.0.1.0.0 (unported) | Request SSL certificates from letsencrypt.org
[mail_environment](mail_environment/) | 9.0.1.0.0 (unported) | Configure mail servers with server_environment_files
[menu_technical_info](menu_technical_info/) | 9.0.1.0.0 (unported) | Fast way to look up technical info about menu item.
[mgmtsystem_kpi](mgmtsystem_kpi/) | 7.0.1.1.1 (unported) | Key Performance Indicator
[qweb_usertime](qweb_usertime/) | 8.0.1.0.0 (unported) | Add user time rendering support in QWeb
[res_config_settings_enterprise_remove](res_config_settings_enterprise_remove/) | 9.0.1.0.0 (unported) | Remove fields in all settings views marked as enterprise
[security_protector](security_protector/) | 0.1 (unported) | Security protector
[server_env_base_external_referentials](server_env_base_external_referentials/) | 1.0 (unported) | Server environment for base_external_referential
[server_environment](server_environment/) | 9.0.1.2.0 (unported) | move some configurations out of the database
[server_environment_files_sample](server_environment_files_sample/) | 9.0.1.0.0 (unported) | sample config file for server_environment
[super_calendar](super_calendar/) | 8.0.0.2.0 (unported) | This module allows to create configurable calendars.
[test_configuration_helper](test_configuration_helper/) | 9.0.1.0.0 (unported) | Configuration Helper - Tests
[users_ldap_groups](users_ldap_groups/) | 8.0.1.2.0 (unported) | Adds user accounts to groups based on rules defined by the administrator.

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-server-tools-10-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-server-tools-10-0)
