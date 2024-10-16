
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=12.0)
[![Pre-commit Status](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml/badge.svg?branch=12.0)](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml?query=branch%3A12.0)
[![Build Status](https://github.com/OCA/server-tools/actions/workflows/test.yml/badge.svg?branch=12.0)](https://github.com/OCA/server-tools/actions/workflows/test.yml?query=branch%3A12.0)
[![codecov](https://codecov.io/gh/OCA/server-tools/branch/12.0/graph/badge.svg)](https://codecov.io/gh/OCA/server-tools)
[![Translation Status](https://translation.odoo-community.org/widgets/server-tools-12-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/server-tools-12-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Tools for server environment

This project aims to deal with modules related to manage Odoo server environment and provide useful tools

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[attachment_delete_restrict](attachment_delete_restrict/) | 12.0.1.0.0 |  | Restrict Deletion of Attachments
[attachment_queue](attachment_queue/) | 12.0.1.0.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Base module adding the concept of queue for processing files
[attachment_synchronize](attachment_synchronize/) | 12.0.2.0.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) [![GSLabIt](https://github.com/GSLabIt.png?size=30px)](https://github.com/GSLabIt) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Attachment Synchronize
[attachment_unindex_content](attachment_unindex_content/) | 12.0.1.0.0 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![ebirbe](https://github.com/ebirbe.png?size=30px)](https://github.com/ebirbe) | Disable indexing of attachments
[auditlog](auditlog/) | 12.0.2.1.1 |  | Audit Log
[auto_backup](auto_backup/) | 12.0.1.0.2 |  | Backups database
[autovacuum_message_attachment](autovacuum_message_attachment/) | 12.0.1.1.1 |  | Automatically delete old mail messages and attachments
[base_changeset](base_changeset/) | 12.0.1.1.2 | [![astirpe](https://github.com/astirpe.png?size=30px)](https://github.com/astirpe) | Track record changesets
[base_conditional_image](base_conditional_image/) | 12.0.1.0.2 |  | Conditional Images
[base_cron_exclusion](base_cron_exclusion/) | 12.0.1.0.0 |  | Allow you to select scheduled actions that should not run simultaneously.
[base_custom_info](base_custom_info/) | 12.0.2.1.0 |  | Add custom field in models
[base_deterministic_session_gc](base_deterministic_session_gc/) | 12.0.1.0.1 |  | Provide a deterministic session garbage collection instead of the default random one
[base_exception](base_exception/) | 12.0.3.1.1 | [![hparfr](https://github.com/hparfr.png?size=30px)](https://github.com/hparfr) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_fontawesome](base_fontawesome/) | 12.0.5.16.0 |  | Up to date Fontawesome resources.
[base_import_module_group](base_import_module_group/) | 12.0.1.0.1 |  | Restrict module importation to specific group
[base_jsonify](base_jsonify/) | 12.0.1.1.2 |  | Base module that provide the jsonify method on all models
[base_kanban_stage](base_kanban_stage/) | 12.0.1.2.2 |  | Provides stage model and abstract logic for inheritance
[base_kanban_stage_state](base_kanban_stage_state/) | 12.0.1.0.0 |  | Maps stages from base_kanban_stage to states
[base_locale_uom_default](base_locale_uom_default/) | 12.0.1.0.1 |  | This provides settings to select default UoMs at the language level.
[base_m2m_custom_field](base_m2m_custom_field/) | 12.0.1.0.0 |  | Customizations of Many2many
[base_model_restrict_update](base_model_restrict_update/) | 12.0.1.1.1 |  | Update Restrict Model
[base_multi_image](base_multi_image/) | 12.0.1.0.1 |  | Allow multiple images for database objects
[base_remote](base_remote/) | 12.0.1.0.2 |  | Remote Base
[base_search_fuzzy](base_search_fuzzy/) | 12.0.1.0.2 |  | Fuzzy search with the PostgreSQL trigram extension
[base_technical_user](base_technical_user/) | 12.0.1.1.1 |  | Add a technical user parameter on the company
[base_view_inheritance_extension](base_view_inheritance_extension/) | 12.0.1.0.1 |  | Adds more operators for view inheritance
[bus_alt_connection](bus_alt_connection/) | 12.0.1.0.0 |  | Needed when using PgBouncer as a connection pooler
[company_country](company_country/) | 12.0.1.2.1 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) | Set country to main company
[configuration_helper](configuration_helper/) | 12.0.1.0.0 |  | Configuration Helper
[cron_inactivity_period](cron_inactivity_period/) | 12.0.1.0.1 |  | Inactivity Periods for Cron Jobs
[database_cleanup](database_cleanup/) | 12.0.1.2.3 |  | Database cleanup
[datetime_formatter](datetime_formatter/) | 12.0.1.0.0 |  | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 12.0.1.0.2 |  | Filter databases with HTTP headers
[excel_import_export](excel_import_export/) | 12.0.1.0.8 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Base module for developing Excel import/export/report
[excel_import_export_demo](excel_import_export_demo/) | 12.0.1.0.3 | [![kittiu](https://github.com/kittiu.png?size=30px)](https://github.com/kittiu) | Excel Import/Export/Report Demo
[fetchmail_incoming_log](fetchmail_incoming_log/) | 12.0.1.0.0 |  | Log all messages received, before they start to be processed.
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 12.0.1.0.0 |  | If fetching mails gives error, send an email to sender
[html_image_url_extractor](html_image_url_extractor/) | 12.0.1.0.0 |  | Extract images found in any HTML field
[html_text](html_text/) | 12.0.1.0.0 |  | Generate excerpts from any HTML field
[iap_alternative_provider](iap_alternative_provider/) | 12.0.1.0.1 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Base module for providing alternative provider for iap apps
[ir_sequence_standard_default](ir_sequence_standard_default/) | 12.0.1.0.0 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![ebirbe](https://github.com/ebirbe.png?size=30px)](https://github.com/ebirbe) | Use Standard implementation of ir.sequence instead of NoGap
[letsencrypt](letsencrypt/) | 12.0.2.0.1 |  | Request SSL certificates from letsencrypt.org
[mail_cleanup](mail_cleanup/) | 12.0.1.0.0 |  | Mark as read or delete mails after a set time
[module_analysis](module_analysis/) | 12.0.1.0.6 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Add analysis tools regarding installed modules to know which installed modules comes from Odoo Core, OCA, or are custom modules
[module_auto_update](module_auto_update/) | 12.0.2.0.7 |  | Automatically update Odoo modules
[module_change_auto_install](module_change_auto_install/) | 12.0.1.0.1 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Customize auto installables modules by configuration
[nsca_client](nsca_client/) | 12.0.1.0.0 |  | Send passive alerts to monitor your Odoo application.
[onchange_helper](onchange_helper/) | 12.0.1.1.0 |  | Technical module that ease execution of onchange in Python code
[profiler](profiler/) | 12.0.1.0.1 | [![thomaspaulb](https://github.com/thomaspaulb.png?size=30px)](https://github.com/thomaspaulb) | profiler
[scheduler_error_mailer](scheduler_error_mailer/) | 12.0.1.2.0 |  | Scheduler Error Mailer
[sentry](sentry/) | 12.0.2.0.3 | [![barsi](https://github.com/barsi.png?size=30px)](https://github.com/barsi) [![naglis](https://github.com/naglis.png?size=30px)](https://github.com/naglis) [![versada](https://github.com/versada.png?size=30px)](https://github.com/versada) [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![fernandahf](https://github.com/fernandahf.png?size=30px)](https://github.com/fernandahf) | Report Odoo errors to Sentry
[slow_statement_logger](slow_statement_logger/) | 12.0.1.0.2 |  | Log slow SQL statements
[sql_export](sql_export/) | 12.0.1.2.1 |  | Export data in csv file with SQL requests
[sql_export_excel](sql_export_excel/) | 12.0.1.1.1 |  | Allow to export a sql query to an excel file.
[sql_export_mail](sql_export_mail/) | 12.0.1.1.0 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Send csv file generated by sql query by mail.
[sql_request_abstract](sql_request_abstract/) | 12.0.1.2.2 |  | Abstract Model to manage SQL Requests

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
