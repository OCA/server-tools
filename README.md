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
[attachment_metadata](attachment_metadata/) | 8.0.1.0.0 | Attachment Metadata
[auditlog](auditlog/) | 8.0.1.3.0 | Audit Log
[auth_admin_passkey](auth_admin_passkey/) | 8.0.2.1.1 | Authentification - Admin Passkey
[auth_brute_force](auth_brute_force/) | 8.0.1.0.0 | Tracks Authentication Attempts and Prevents Brute-force Attacks module
[auth_dynamic_groups](auth_dynamic_groups/) | 8.0.1.0.0 | Have membership conditions for certain groups
[auth_from_http_remote_user](auth_from_http_remote_user/) | 8.0.1.0.0 | Authenticate via HTTP Remote User
[auth_signup_verify_email](auth_signup_verify_email/) | 8.0.1.0.0 | Force uninvited users to use a good email for signup
[auth_supplier](auth_supplier/) | 8.0.1.0.0 | Auth Supplier
[auto_backup](auto_backup/) | 8.0.1.0.3 | Backups database
[base_concurrency](base_concurrency/) | 8.0.1.1.0 | Base Concurrency
[base_custom_info](base_custom_info/) | 8.0.1.0.0 | Add custom field in models
[base_debug4all](base_debug4all/) | 8.0.1.0.0 | Shows full debug options for all users
[base_export_manager](base_export_manager/) | 8.0.2.1.0 | Manage model export profiles
[base_external_dbsource](base_external_dbsource/) | 8.0.1.3.0 | External Database Sources
[base_field_validator](base_field_validator/) | 8.0.1.0.0 | Validate fields using regular expressions
[base_import_match](base_import_match/) | 8.0.1.0.1 | Try to avoid duplicates before importing
[base_import_odoo](base_import_odoo/) | 8.0.1.0.1 | Import records from another Odoo instance
[base_import_security_group](base_import_security_group/) | 8.0.1.0.0 | Group-based permissions for importing CSV files
[base_ir_filters_active](base_ir_filters_active/) | 8.0.1.0.0 | Allows you to disable (hide) filters
[base_manifest_extension](base_manifest_extension/) | 8.0.1.0.0 | Adds some useful keys to manifest files
[base_mixin_restrict_field_access](base_mixin_restrict_field_access/) | 8.0.1.0.0 | Make it simple to restrict read and/or write access to certain fields base on some condition
[base_module_doc_rst](base_module_doc_rst/) | 8.0.1.0.0 | Modules Technical Guides in RST and Relationship Graphs
[base_multi_image](base_multi_image/) | 8.0.2.0.0 | Allow multiple images for database objects
[base_name_search_improved](base_name_search_improved/) | 8.0.1.0.2 | Friendlier search when typing in relation fields
[base_optional_quick_create](base_optional_quick_create/) | 8.0.0.1.0 | Avoid 'quick create' on m2o fields, on a 'by model' basis
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 8.0.1.0.0 | Report qweb auto generation
[base_search_fuzzy](base_search_fuzzy/) | 8.0.1.0.0 | Fuzzy search with the PostgreSQL trigram extension
[base_suspend_security](base_suspend_security/) | 8.0.1.0.1 | Suspend security checks for a call
[base_user_gravatar](base_user_gravatar/) | 8.0.1.0.0 | Synchronize Gravatar image
[base_user_reset_access](base_user_reset_access/) | 8.0.1.0.0 | Reset User Access Right
[base_user_role](base_user_role/) | 8.0.1.2.0 | User roles
[base_view_inheritance_extension](base_view_inheritance_extension/) | 8.0.1.0.0 | Adds more operators for view inheritance
[cron_run_manually](cron_run_manually/) | 8.0.1.0.0 | Call cron jobs from their form view
[database_cleanup](database_cleanup/) | 8.0.0.1.0 | Database cleanup
[datetime_formatter](datetime_formatter/) | 8.0.1.0.0 | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 8.0.1.0.1 | dbfilter_from_header
[dead_mans_switch_client](dead_mans_switch_client/) | 8.0.1.0.1 | Be notified when customers' odoo instances go down
[dead_mans_switch_server](dead_mans_switch_server/) | 8.0.1.0.0 | Be notified when customers' odoo instances go down
[disable_openerp_online](disable_openerp_online/) | 8.0.1.1.0 | Remove odoo.com bindings
[fetchmail_attach_from_folder](fetchmail_attach_from_folder/) | 8.0.1.0.1 | Attach mails in an IMAP folder to existing objects
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 8.0.1.0.1 | If fetching mails gives error, send an email to sender
[field_char_transformed](field_char_transformed/) | 8.0.1.0.0 | Allows to transform input in character fields before writing or reading it to/from the database
[field_rrule](field_rrule/) | 8.0.1.0.1 | Provides a field and widget for RRules according to RFC 2445
[html_image_url_extractor](html_image_url_extractor/) | 8.0.1.0.0 | Extract images found in any HTML field
[html_text](html_text/) | 8.0.1.0.0 | Generate excerpts from any HTML field
[import_odbc](import_odbc/) | 8.0.0.1.3 | Import data from SQL and ODBC data sources.
[inactive_session_timeout](inactive_session_timeout/) | 8.0.1.0.0 | This module disable all inactive sessions since a given delay
[language_path_mixin](language_path_mixin/) | 8.0.1.0.0 | Setting the partner's language in RML reports
[letsencrypt](letsencrypt/) | 8.0.1.0.0 | Request SSL certificates from letsencrypt.org
[log_forwarded_for_ip](log_forwarded_for_ip/) | 8.0.1.0.0 | Displays source IPs in log when behind a reverse proxy
[logging_json](logging_json/) | 8.0.1.0.0 | JSON Logging
[mail_environment](mail_environment/) | 8.0.0.1.0 | Server env config for mail + fetchmail
[mass_editing](mass_editing/) | 8.0.1.3.0 | Mass Editing
[mass_sorting](mass_sorting/) | 8.0.1.0.0 | Sort any models by any fields list
[module_auto_update](module_auto_update/) | 8.0.2.0.3 | Automatically update Odoo modules
[module_prototyper](module_prototyper/) | 8.0.0.3.0 | Prototype your module.
[module_uninstall_check](module_uninstall_check/) | 8.0.1.0.0 | Add Extra Checks before uninstallation of modules
[password_security](password_security/) | 8.0.1.1.2 | Allow admin to set password security requirements.
[profiler](profiler/) | 8.0.1.0.0 | profiler
[qweb_usertime](qweb_usertime/) | 8.0.1.0.0 | Add user time rendering support in QWeb
[save_translation_file](save_translation_file/) | 8.0.1.0.0 | Allows developpers to easily generate i18n files
[scheduler_error_mailer](scheduler_error_mailer/) | 8.0.1.0.0 | Send an e-mail when a scheduler fails
[secure_uninstall](secure_uninstall/) | 8.0.1.0.0 | Ask password to authorize uninstall
[sentry](sentry/) | 8.0.1.0.0 | Report Odoo errors to Sentry
[server_environment](server_environment/) | 8.0.1.1.0 | server configuration environment files
[server_environment_files_sample](server_environment_files_sample/) | 8.0.1.0.0 | Example server configuration environment files repository module
[shell](shell/) | 8.0.1.0.0 | Backport of the v9 shell CLI command.
[sql_export](sql_export/) | 8.0.1.0.0 | Export data in csv file with SQL requests
[sql_request_abstract](sql_request_abstract/) | 8.0.1.0.1 | Abstract Model to manage SQL Requests
[super_calendar](super_calendar/) | 8.0.0.2.0 | This module allows to create configurable calendars.
[users_ldap_groups](users_ldap_groups/) | 8.0.1.2.2 | Adds user accounts to groups based on rules defined by the administrator.
[users_ldap_mail](users_ldap_mail/) | 8.0.1.0.0 | LDAP mapping for user name and e-mail
[users_ldap_populate](users_ldap_populate/) | 8.0.1.2.1 | Create users from LDAP before they log in
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
[ir_config_parameter_viewer](ir_config_parameter_viewer/) | 0.1 (unported) | Ir.config_parameter view
[security_protector](security_protector/) | 0.1 (unported) | Security protector
[server_env_base_external_referentials](server_env_base_external_referentials/) | 1.0 (unported) | Server environment for base_external_referential

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-server-tools-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-server-tools-8-0)
