[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/149/14.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-server-tools-149)
[![Build Status](https://travis-ci.com/OCA/server-tools.svg?branch=14.0)](https://travis-ci.com/OCA/server-tools)
[![codecov](https://codecov.io/gh/OCA/server-tools/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/server-tools)
[![Translation Status](https://translation.odoo-community.org/widgets/server-tools-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/server-tools-14-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Tools for server environment(s)

This project aims to deal with modules related to manage Odoo server environment and provide useful tools.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[attachment_unindex_content](attachment_unindex_content/) | 14.0.1.0.0 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![ebirbe](https://github.com/ebirbe.png?size=30px)](https://github.com/ebirbe) | Disable indexing of attachments
[auditlog](auditlog/) | 14.0.1.2.0 |  | Audit Log
[auto_backup](auto_backup/) | 14.0.1.0.0 |  | Backups database
[autovacuum_message_attachment](autovacuum_message_attachment/) | 14.0.1.0.0 |  | Automatically delete old mail messages and attachments
[base_changeset](base_changeset/) | 14.0.1.0.1 | [![astirpe](https://github.com/astirpe.png?size=30px)](https://github.com/astirpe) | Track record changesets
[base_cron_exclusion](base_cron_exclusion/) | 14.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allow you to select scheduled actions that should not run simultaneously.
[base_custom_info](base_custom_info/) | 14.0.1.0.1 |  | Add custom field in models
[base_exception](base_exception/) | 14.0.1.1.0 |  | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_jsonify](base_jsonify/) | 14.0.1.4.1 |  | Base module that provide the jsonify method on all models
[base_kanban_stage](base_kanban_stage/) | 14.0.1.0.0 |  | Provides stage model and abstract logic for inheritance
[base_kanban_stage_state](base_kanban_stage_state/) | 14.0.1.0.0 |  | Maps stages from base_kanban_stage to states
[base_m2m_custom_field](base_m2m_custom_field/) | 14.0.1.1.0 |  | Customizations of Many2many
[base_model_restrict_update](base_model_restrict_update/) | 14.0.1.0.0 |  | Update Restrict Model
[base_name_search_improved](base_name_search_improved/) | 14.0.1.0.0 |  | Friendlier search when typing in relation fields
[base_name_search_multi_lang](base_name_search_multi_lang/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Name search by multiple active language
[base_remote](base_remote/) | 14.0.1.0.0 |  | Remote Base
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 14.0.1.0.1 |  | Report qweb auto generation
[base_search_fuzzy](base_search_fuzzy/) | 14.0.1.0.1 |  | Fuzzy search with the PostgreSQL trigram extension
[base_sequence_option](base_sequence_option/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Alternative sequence options for specific models
[base_sparse_field_list_support](base_sparse_field_list_support/) | 14.0.1.0.1 |  | add list support to convert_to_cache()
[base_technical_user](base_technical_user/) | 14.0.1.0.0 |  | Add a technical user parameter on the company
[base_time_window](base_time_window/) | 14.0.1.0.1 |  | Base model to handle time windows
[base_video_link](base_video_link/) | 14.0.1.1.1 |  | Add the possibility to link video on record
[base_view_inheritance_extension](base_view_inheritance_extension/) | 14.0.1.1.0 |  | Adds more operators for view inheritance
[configuration_helper](configuration_helper/) | 14.0.1.0.0 |  | Configuration Helper
[datetime_formatter](datetime_formatter/) | 14.0.1.0.0 |  | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 14.0.1.0.0 |  | Filter databases with HTTP headers
[excel_import_export](excel_import_export/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Base module for developing Excel import/export/report
[excel_import_export_demo](excel_import_export_demo/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Excel Import/Export/Report Demo
[fetchmail_incoming_log](fetchmail_incoming_log/) | 14.0.1.0.0 |  | Log all messages received, before they start to be processed.
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 14.0.1.0.0 |  | If fetching mails gives error, send an email to sender
[fetchmail_notify_error_to_sender_test](fetchmail_notify_error_to_sender_test/) | 14.0.1.0.0 |  | Test for Fetchmail Notify Error to Sender
[html_image_url_extractor](html_image_url_extractor/) | 14.0.1.0.0 |  | Extract images found in any HTML field
[html_text](html_text/) | 14.0.1.0.0 |  | Generate excerpts from any HTML field
[iap_alternative_provider](iap_alternative_provider/) | 14.0.1.0.0 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Base module for providing alternative provider for iap apps
[letsencrypt](letsencrypt/) | 14.0.1.0.0 |  | Request SSL certificates from letsencrypt.org
[module_auto_update](module_auto_update/) | 14.0.1.0.1 |  | Automatically update Odoo modules
[module_change_auto_install](module_change_auto_install/) | 14.0.1.0.3 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Customize auto installables modules by configuration
[module_prototyper](module_prototyper/) | 14.0.1.0.0 |  | Prototype your module.
[onchange_helper](onchange_helper/) | 14.0.1.0.0 |  | Technical module that ease execution of onchange in Python code
[scheduler_error_mailer](scheduler_error_mailer/) | 14.0.1.0.0 |  | Scheduler Error Mailer
[sentry](sentry/) | 14.0.1.0.2 |  | Report Odoo errors to Sentry
[sequence_python](sequence_python/) | 14.0.1.0.0 |  | Calculate a sequence number from a Python expression
[slow_statement_logger](slow_statement_logger/) | 14.0.1.0.1 |  | Log slow SQL statements
[sql_export](sql_export/) | 14.0.1.1.0 |  | Export data in csv file with SQL requests
[sql_export_excel](sql_export_excel/) | 14.0.1.1.0 |  | Allow to export a sql query to an excel file.
[sql_export_mail](sql_export_mail/) | 14.0.1.0.0 |  | Send csv file generated by sql query by mail.
[sql_request_abstract](sql_request_abstract/) | 14.0.1.1.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Abstract Model to manage SQL Requests
[test_base_time_window](test_base_time_window/) | 14.0.1.0.1 |  | Test Base model to handle time windows
[upgrade_analysis](upgrade_analysis/) | 14.0.2.2.0 |  | Performs a difference analysis between modules installed on two different Odoo instances

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
