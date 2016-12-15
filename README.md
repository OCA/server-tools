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
[admin_technical_features](admin_technical_features/) | 9.0.0.1.0 | Checks the technical features box for admin user.
[attachment_base_synchronize](attachment_base_synchronize/) | 9.0.1.0.0 | Attachment Base Synchronize
[auditlog](auditlog/) | 9.0.1.0.0 | Audit Log
[auth_from_http_remote_user](auth_from_http_remote_user/) | 9.0.1.0.0 | Authenticate via HTTP Remote User
[auth_session_timeout](auth_session_timeout/) | 9.0.1.0.0 | This module disable all inactive sessions since a given delay
[auth_signup_verify_email](auth_signup_verify_email/) | 9.0.1.0.0 | Force uninvited users to use a good email for signup
[auth_supplier](auth_supplier/) | 9.0.2.0.0 | Auth Supplier
[base_custom_info](base_custom_info/) | 9.0.1.0.0 | Add custom field in models
[base_export_manager](base_export_manager/) | 9.0.1.1.0 | Manage model export profiles
[base_external_dbsource](base_external_dbsource/) | 9.0.1.0.0 | External Database Sources
[base_multi_image](base_multi_image/) | 9.0.1.1.0 | Allow multiple images for database objects
[base_name_search_improved](base_name_search_improved/) | 9.0.1.0.0 | Friendlier search when typing in relation fields
[base_optional_quick_create](base_optional_quick_create/) | 9.0.1.0.0 | Avoid 'quick create' on m2o fields, on a 'by model' basis
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 9.0.1.0.0 | Report qweb auto generation
[base_suspend_security](base_suspend_security/) | 9.0.1.0.0 | Suspend security checks for a call
[base_technical_features](base_technical_features/) | 9.0.1.0.0 | Access to technical features without activating debug mode
[base_user_gravatar](base_user_gravatar/) | 9.0.1.0.0 | Synchronize Gravatar Image
[configuration_helper](configuration_helper/) | 9.0.1.0.0 | Configuration Helper
[database_cleanup](database_cleanup/) | 9.0.1.0.0 | Database cleanup
[date_range](date_range/) | 9.0.1.0.0 | Manage all kind of date range
[datetime_formatter](datetime_formatter/) | 9.0.1.0.0 | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 9.0.1.0.0 | Filter databases with HTTP headers
[dead_mans_switch_client](dead_mans_switch_client/) | 9.0.1.0.1 | Be notified when customers' odoo instances go down
[disable_odoo_online](disable_odoo_online/) | 9.0.1.0.0 | Remove odoo.com bindings
[html_image_url_extractor](html_image_url_extractor/) | 9.0.1.0.0 | Extract images found in any HTML field
[html_text](html_text/) | 9.0.1.0.0 | Generate excerpts from any HTML field
[kpi](kpi/) | 9.0.1.0.0 | Key Performance Indicator
[letsencrypt](letsencrypt/) | 9.0.1.0.0 | Request SSL certificates from letsencrypt.org
[mail_cleanup](mail_cleanup/) | 9.0.1.0.0 | Mark as read or delete mails after a set time
[mail_environment](mail_environment/) | 9.0.1.0.0 | Configure mail servers with server_environment_files
[mass_editing](mass_editing/) | 9.0.1.0.0 | Mass Editing
[menu_technical_info](menu_technical_info/) | 9.0.1.0.0 | Fast way to look up technical info about menu item.
[module_prototyper](module_prototyper/) | 9.0.0.1.0 | Prototype your module.
[password_security](password_security/) | 9.0.1.0.2 | Allow admin to set password security requirements.
[res_config_settings_enterprise_remove](res_config_settings_enterprise_remove/) | 9.0.1.0.0 | Remove fields in all settings views marked as enterprise
[scheduler_error_mailer](scheduler_error_mailer/) | 9.0.1.0.0 | Scheduler Error Mailer
[server_environment](server_environment/) | 9.0.1.2.0 | move some configurations out of the database
[server_environment_files_sample](server_environment_files_sample/) | 9.0.1.0.0 | sample config file for server_environment
[test_configuration_helper](test_configuration_helper/) | 9.0.1.0.0 | Configuration Helper - Tests
[users_ldap_mail](users_ldap_mail/) | 9.0.1.0.0 | LDAP mapping for user name and e-mail
[users_ldap_populate](users_ldap_populate/) | 9.0.1.0.0 | LDAP Populate

Unported addons
---------------
addon | version | summary
--- | --- | ---
[auth_admin_passkey](auth_admin_passkey/) | 8.0.2.1.1 (unported) | Authentification - Admin Passkey
[auth_dynamic_groups](auth_dynamic_groups/) | 8.0.1.0.0 (unported) | Have membership conditions for certain groups
[auth_from_http_basic](auth_from_http_basic/) | 1.0 (unported) | Authenticate via HTTP basic authentication
[auth_from_http_basic_logout](auth_from_http_basic_logout/) | 1.0 (unported) | Authenticate via HTTP basic authentication (logout helper)
[email_template_template](email_template_template/) | 1.0 (unported) | Templates for email templates
[fetchmail_attach_from_folder](fetchmail_attach_from_folder/) | 8.0.1.0.1 (unported) | Attach mails in an IMAP folder to existing objects
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 8.0.1.0.0 (unported) | If fetching mails gives error, send an email to sender
[import_odbc](import_odbc/) | 1.3 (unported) | Import data from SQL and ODBC data sources.
[ir_config_parameter_viewer](ir_config_parameter_viewer/) | 0.1 (unported) | Ir.config_parameter view
[language_path_mixin](language_path_mixin/) | 8.0.1.0.0 (unported) | Setting the partner's language in RML reports
[qweb_usertime](qweb_usertime/) | 8.0.1.0.0 (unported) | Add user time rendering support in QWeb
[security_protector](security_protector/) | 0.1 (unported) | Security protector
[server_env_base_external_referentials](server_env_base_external_referentials/) | 1.0 (unported) | Server environment for base_external_referential
[super_calendar](super_calendar/) | 8.0.0.2.0 (unported) | This module allows to create configurable calendars.
[users_ldap_groups](users_ldap_groups/) | 8.0.1.2.0 (unported) | Adds user accounts to groups based on rules defined by the administrator.
[web_context_tunnel](web_context_tunnel/) | 8.0.2.0.0 (unported) | Web Context Tunnel

[//]: # (end addons)

Translation Status
------------------
[![Transifex Status](https://www.transifex.com/projects/p/OCA-server-tools-9-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-server-tools-9-0)
