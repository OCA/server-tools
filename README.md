
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=14.0)
[![Pre-commit Status](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml/badge.svg?branch=14.0)](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml?query=branch%3A14.0)
[![Build Status](https://github.com/OCA/server-tools/actions/workflows/test.yml/badge.svg?branch=14.0)](https://github.com/OCA/server-tools/actions/workflows/test.yml?query=branch%3A14.0)
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
[attachment_delete_restrict](attachment_delete_restrict/) | 14.0.1.0.0 | [![yostashiro](https://github.com/yostashiro.png?size=30px)](https://github.com/yostashiro) [![Kev-Roche](https://github.com/Kev-Roche.png?size=30px)](https://github.com/Kev-Roche) | Restrict Deletion of Attachments
[attachment_queue](attachment_queue/) | 14.0.1.0.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Base module adding the concept of queue for processing files
[attachment_synchronize](attachment_synchronize/) | 14.0.1.0.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![GSLabIt](https://github.com/GSLabIt.png?size=30px)](https://github.com/GSLabIt) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Attachment Synchronize
[attachment_unindex_content](attachment_unindex_content/) | 14.0.1.0.1 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![ebirbe](https://github.com/ebirbe.png?size=30px)](https://github.com/ebirbe) [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) | Disable indexing of attachments
[auditlog](auditlog/) | 14.0.1.3.0 |  | Audit Log
[auto_backup](auto_backup/) | 14.0.1.0.0 |  | Backups database
[autovacuum_message_attachment](autovacuum_message_attachment/) | 14.0.1.0.0 |  | Automatically delete old mail messages and attachments
[base_changeset](base_changeset/) | 14.0.1.1.3 | [![astirpe](https://github.com/astirpe.png?size=30px)](https://github.com/astirpe) | Track record changesets
[base_conditional_image](base_conditional_image/) | 14.0.1.0.0 |  | This module extends the functionality to support conditional images
[base_cron_exclusion](base_cron_exclusion/) | 14.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | Allow you to select scheduled actions that should not run simultaneously.
[base_custom_info](base_custom_info/) | 14.0.1.0.1 |  | Add custom field in models
[base_deterministic_session_gc](base_deterministic_session_gc/) | 14.0.1.0.0 |  | Provide a deterministic session garbage collection instead of the default random one
[base_exception](base_exception/) | 14.0.2.1.0 | [![hparfr](https://github.com/hparfr.png?size=30px)](https://github.com/hparfr) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_fontawesome](base_fontawesome/) | 14.0.5.15.4 |  | Up to date Fontawesome resources.
[base_generate_code](base_generate_code/) | 14.0.1.0.1 | [![Kev-Roche](https://github.com/Kev-Roche.png?size=30px)](https://github.com/Kev-Roche) | Code Generator
[base_jsonify](base_jsonify/) | 14.0.2.0.0 |  | Base module that provide the jsonify method on all models. WARNING: since version 14.0.2.0.0 the module have been renamed to `jsonifier`. This module now depends on it only for backward compatibility. It will be discarded in v15 likely.
[base_kanban_stage](base_kanban_stage/) | 14.0.1.0.0 |  | Provides stage model and abstract logic for inheritance
[base_kanban_stage_state](base_kanban_stage_state/) | 14.0.1.0.0 |  | Maps stages from base_kanban_stage to states
[base_m2m_custom_field](base_m2m_custom_field/) | 14.0.1.1.0 |  | Customizations of Many2many
[base_model_restrict_update](base_model_restrict_update/) | 14.0.1.0.0 |  | Update Restrict Model
[base_multi_image](base_multi_image/) | 14.0.1.0.0 |  | Allow multiple images for database objects
[base_name_search_improved](base_name_search_improved/) | 14.0.1.1.0 |  | Friendlier search when typing in relation fields
[base_name_search_multi_lang](base_name_search_multi_lang/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Name search by multiple active language
[base_remote](base_remote/) | 14.0.1.0.0 |  | Remote Base
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 14.0.1.0.1 |  | Report qweb auto generation
[base_search_fuzzy](base_search_fuzzy/) | 14.0.1.0.2 |  | Fuzzy search with the PostgreSQL trigram extension
[base_sequence_option](base_sequence_option/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Alternative sequence options for specific models
[base_sparse_field_list_support](base_sparse_field_list_support/) | 14.0.1.0.1 |  | add list support to convert_to_cache()
[base_technical_user](base_technical_user/) | 14.0.1.0.0 |  | Add a technical user parameter on the company
[base_time_dependent_parameter](base_time_dependent_parameter/) | 14.0.1.0.1 | [![appstogrow](https://github.com/appstogrow.png?size=30px)](https://github.com/appstogrow) [![nimarosa](https://github.com/nimarosa.png?size=30px)](https://github.com/nimarosa) | Time dependent parameters Adds the feature to define parameters with time based versions.
[base_time_window](base_time_window/) | 14.0.1.0.1 |  | Base model to handle time windows
[base_video_link](base_video_link/) | 14.0.1.1.1 |  | Add the possibility to link video on record
[base_view_inheritance_extension](base_view_inheritance_extension/) | 14.0.1.1.1 |  | Adds more operators for view inheritance
[bus_alt_connection](bus_alt_connection/) | 14.0.1.0.0 |  | Needed when using PgBouncer as a connection pooler
[configuration_helper](configuration_helper/) | 14.0.1.0.0 |  | Configuration Helper
[database_cleanup](database_cleanup/) | 14.0.1.0.0 |  | Database cleanup
[datetime_formatter](datetime_formatter/) | 14.0.1.0.0 |  | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 14.0.1.0.0 |  | Filter databases with HTTP headers
[excel_import_export](excel_import_export/) | 14.0.1.1.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Base module for developing Excel import/export/report
[excel_import_export_demo](excel_import_export_demo/) | 14.0.1.0.0 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Excel Import/Export/Report Demo
[fetchmail_incoming_log](fetchmail_incoming_log/) | 14.0.1.0.0 |  | Log all messages received, before they start to be processed.
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 14.0.1.0.0 |  | If fetching mails gives error, send an email to sender
[fetchmail_notify_error_to_sender_test](fetchmail_notify_error_to_sender_test/) | 14.0.1.0.0 |  | Test for Fetchmail Notify Error to Sender
[html_image_url_extractor](html_image_url_extractor/) | 14.0.1.0.0 |  | Extract images found in any HTML field
[html_text](html_text/) | 14.0.1.0.0 |  | Generate excerpts from any HTML field
[iap_alternative_provider](iap_alternative_provider/) | 14.0.1.0.0 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Base module for providing alternative provider for iap apps
[jsonifier](jsonifier/) | 14.0.1.0.1 |  | JSON-ify data for all models
[letsencrypt](letsencrypt/) | 14.0.1.0.0 |  | Request SSL certificates from letsencrypt.org
[module_auto_update](module_auto_update/) | 14.0.1.0.1 |  | Automatically update Odoo modules
[module_change_auto_install](module_change_auto_install/) | 14.0.1.0.3 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Customize auto installables modules by configuration
[module_prototyper](module_prototyper/) | 14.0.1.0.0 |  | Prototype your module.
[onchange_helper](onchange_helper/) | 14.0.1.0.2 |  | Technical module that ease execution of onchange in Python code
[rpc_helper](rpc_helper/) | 14.0.1.1.0 | [![simahawk](https://github.com/simahawk.png?size=30px)](https://github.com/simahawk) | Helpers for disabling RPC calls
[scheduler_error_mailer](scheduler_error_mailer/) | 14.0.1.2.0 |  | Scheduler Error Mailer
[sentry](sentry/) | 14.0.1.1.1 | [![barsi](https://github.com/barsi.png?size=30px)](https://github.com/barsi) [![naglis](https://github.com/naglis.png?size=30px)](https://github.com/naglis) [![versada](https://github.com/versada.png?size=30px)](https://github.com/versada) [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![fernandahf](https://github.com/fernandahf.png?size=30px)](https://github.com/fernandahf) | Report Odoo errors to Sentry
[sequence_python](sequence_python/) | 14.0.1.0.0 |  | Calculate a sequence number from a Python expression
[slow_statement_logger](slow_statement_logger/) | 14.0.1.0.1 |  | Log slow SQL statements
[sql_export](sql_export/) | 14.0.1.2.1 |  | Export data in csv file with SQL requests
[sql_export_excel](sql_export_excel/) | 14.0.1.1.0 |  | Allow to export a sql query to an excel file.
[sql_export_mail](sql_export_mail/) | 14.0.1.0.0 |  | Send csv file generated by sql query by mail.
[sql_request_abstract](sql_request_abstract/) | 14.0.1.3.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Abstract Model to manage SQL Requests
[test_base_time_window](test_base_time_window/) | 14.0.1.0.1 |  | Test Base model to handle time windows
[upgrade_analysis](upgrade_analysis/) | 14.0.2.2.1 |  | Performs a difference analysis between modules installed on two different Odoo instances

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
