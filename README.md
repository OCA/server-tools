
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
[attachment_delete_restrict](attachment_delete_restrict/) | 14.0.1.0.2 | <a href='https://github.com/yostashiro'><img src='https://github.com/yostashiro.png' width='32' height='32' style='border-radius:50%;' alt='yostashiro'/></a> <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> | Restrict Deletion of Attachments
[attachment_queue](attachment_queue/) | 14.0.1.0.2 | <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Base module adding the concept of queue for processing files
[attachment_synchronize](attachment_synchronize/) | 14.0.1.0.3 | <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> <a href='https://github.com/GSLabIt'><img src='https://github.com/GSLabIt.png' width='32' height='32' style='border-radius:50%;' alt='GSLabIt'/></a> <a href='https://github.com/bealdav'><img src='https://github.com/bealdav.png' width='32' height='32' style='border-radius:50%;' alt='bealdav'/></a> | Attachment Synchronize
[attachment_unindex_content](attachment_unindex_content/) | 14.0.1.0.1 | <a href='https://github.com/moylop260'><img src='https://github.com/moylop260.png' width='32' height='32' style='border-radius:50%;' alt='moylop260'/></a> <a href='https://github.com/ebirbe'><img src='https://github.com/ebirbe.png' width='32' height='32' style='border-radius:50%;' alt='ebirbe'/></a> <a href='https://github.com/luisg123v'><img src='https://github.com/luisg123v.png' width='32' height='32' style='border-radius:50%;' alt='luisg123v'/></a> | Disable indexing of attachments
[auditlog](auditlog/) | 14.0.2.0.2 |  | Audit Log
[auto_backup](auto_backup/) | 14.0.1.0.1 |  | Backups database
[autovacuum_message_attachment](autovacuum_message_attachment/) | 14.0.1.0.1 |  | Automatically delete old mail messages and attachments
[base_changeset](base_changeset/) | 14.0.2.0.2 | <a href='https://github.com/astirpe'><img src='https://github.com/astirpe.png' width='32' height='32' style='border-radius:50%;' alt='astirpe'/></a> | Track record changesets
[base_conditional_image](base_conditional_image/) | 14.0.2.0.1 |  | This module extends the functionality to support conditional images
[base_contextvars](base_contextvars/) | 14.0.1.0.4 | <a href='https://github.com/sbidoul'><img src='https://github.com/sbidoul.png' width='32' height='32' style='border-radius:50%;' alt='sbidoul'/></a> | Patch Odoo threadlocals to use contextvars instead.
[base_cron_exclusion](base_cron_exclusion/) | 14.0.1.0.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Allow you to select scheduled actions that should not run simultaneously.
[base_custom_info](base_custom_info/) | 14.0.1.0.3 |  | Add custom field in models
[base_deterministic_session_gc](base_deterministic_session_gc/) | 14.0.1.0.0 |  | Provide a deterministic session garbage collection instead of the default random one
[base_exception](base_exception/) | 14.0.2.1.1 | <a href='https://github.com/hparfr'><img src='https://github.com/hparfr.png' width='32' height='32' style='border-radius:50%;' alt='hparfr'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_fontawesome](base_fontawesome/) | 14.0.5.15.5 |  | Up to date Fontawesome resources.
[base_force_record_noupdate](base_force_record_noupdate/) | 14.0.1.0.0 |  | Manually force noupdate=True on models
[base_future_response](base_future_response/) | 14.0.1.0.2 | <a href='https://github.com/sbidoul'><img src='https://github.com/sbidoul.png' width='32' height='32' style='border-radius:50%;' alt='sbidoul'/></a> | Backport Odoo 16 FutureReponse mechanism.
[base_generate_code](base_generate_code/) | 14.0.1.1.1 | <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> | Code Generator
[base_import_odoo](base_import_odoo/) | 14.0.1.0.0 |  | Import records from another Odoo instance
[base_jsonify](base_jsonify/) | 14.0.2.0.0 |  | Base module that provide the jsonify method on all models. WARNING: since version 14.0.2.0.0 the module have been renamed to `jsonifier`. This module now depends on it only for backward compatibility. It will be discarded in v15 likely.
[base_kanban_stage](base_kanban_stage/) | 14.0.1.0.2 |  | Provides stage model and abstract logic for inheritance
[base_kanban_stage_state](base_kanban_stage_state/) | 14.0.1.0.0 |  | Maps stages from base_kanban_stage to states
[base_m2m_custom_field](base_m2m_custom_field/) | 14.0.1.1.0 |  | Customizations of Many2many
[base_model_restrict_update](base_model_restrict_update/) | 14.0.1.1.0 |  | Update Restrict Model
[base_multi_image](base_multi_image/) | 14.0.1.0.1 |  | Allow multiple images for database objects
[base_name_search_improved](base_name_search_improved/) | 14.0.1.1.2 |  | Friendlier search when typing in relation fields
[base_name_search_multi_lang](base_name_search_multi_lang/) | 14.0.1.0.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Name search by multiple active language
[base_order_by_related](base_order_by_related/) | 14.0.1.0.0 | <a href='https://github.com/thomaspaulb'><img src='https://github.com/thomaspaulb.png' width='32' height='32' style='border-radius:50%;' alt='thomaspaulb'/></a> | Order by non-stored related fields
[base_remote](base_remote/) | 14.0.1.0.1 |  | Remote Base
[base_report_auto_create_qweb](base_report_auto_create_qweb/) | 14.0.1.0.1 |  | Report qweb auto generation
[base_search_fuzzy](base_search_fuzzy/) | 14.0.1.0.3 |  | Fuzzy search with the PostgreSQL trigram extension
[base_sequence_default](base_sequence_default/) | 14.0.1.0.0 | <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> <a href='https://github.com/yajo'><img src='https://github.com/yajo.png' width='32' height='32' style='border-radius:50%;' alt='yajo'/></a> | Use sequences for default values of fields when creating a new record
[base_sequence_option](base_sequence_option/) | 14.0.1.0.1 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Alternative sequence options for specific models
[base_sparse_field_list_support](base_sparse_field_list_support/) | 14.0.1.0.1 |  | add list support to convert_to_cache()
[base_technical_user](base_technical_user/) | 14.0.1.0.2 |  | Add a technical user parameter on the company
[base_time_parameter](base_time_parameter/) | 14.0.3.1.1 | <a href='https://github.com/appstogrow'><img src='https://github.com/appstogrow.png' width='32' height='32' style='border-radius:50%;' alt='appstogrow'/></a> <a href='https://github.com/nimarosa'><img src='https://github.com/nimarosa.png' width='32' height='32' style='border-radius:50%;' alt='nimarosa'/></a> | Time dependent parameters Adds the feature to define parameters with time based versions.
[base_time_window](base_time_window/) | 14.0.1.0.1 |  | Base model to handle time windows
[base_video_link](base_video_link/) | 14.0.1.1.2 |  | Add the possibility to link video on record
[base_view_full_arch](base_view_full_arch/) | 14.0.1.0.0 |  | Allows displaying the full, compiled architecture for all views
[base_view_inheritance_extension](base_view_inheritance_extension/) | 14.0.2.0.1 |  | Adds more operators for view inheritance
[bus_alt_connection](bus_alt_connection/) | 14.0.1.0.0 |  | Needed when using PgBouncer as a connection pooler
[configuration_helper](configuration_helper/) | 14.0.1.0.1 |  | Configuration Helper
[cron_daylight_saving_time_resistant](cron_daylight_saving_time_resistant/) | 14.0.1.0.0 |  | Run cron on fixed hours
[database_cleanup](database_cleanup/) | 14.0.1.1.2 |  | Database cleanup
[datetime_formatter](datetime_formatter/) | 14.0.1.0.0 |  | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 14.0.1.0.1 |  | Filter databases with HTTP headers
[excel_import_export](excel_import_export/) | 14.0.1.1.2 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Base module for developing Excel import/export/report
[excel_import_export_demo](excel_import_export_demo/) | 14.0.1.0.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Excel Import/Export/Report Demo
[fetchmail_incoming_log](fetchmail_incoming_log/) | 14.0.1.0.0 |  | Log all messages received, before they start to be processed.
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 14.0.1.0.0 |  | If fetching mails gives error, send an email to sender
[fetchmail_notify_error_to_sender_test](fetchmail_notify_error_to_sender_test/) | 14.0.1.0.0 |  | Test for Fetchmail Notify Error to Sender
[html_image_url_extractor](html_image_url_extractor/) | 14.0.1.0.1 |  | Extract images found in any HTML field
[html_text](html_text/) | 14.0.1.0.1 |  | Generate excerpts from any HTML field
[iap_alternative_provider](iap_alternative_provider/) | 14.0.1.0.0 | <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Base module for providing alternative provider for iap apps
[jsonifier](jsonifier/) | 14.0.1.2.3 |  | JSON-ify data for all models
[jsonifier_stored](jsonifier_stored/) | 14.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> <a href='https://github.com/mmequignon'><img src='https://github.com/mmequignon.png' width='32' height='32' style='border-radius:50%;' alt='mmequignon'/></a> | Pre-compute and store JSON data on any model
[letsencrypt](letsencrypt/) | 14.0.1.0.2 |  | Request SSL certificates from letsencrypt.org
[mail_cleanup](mail_cleanup/) | 14.0.1.0.0 |  | Mark as read or delete mails after a set time
[model_read_only](model_read_only/) | 14.0.3.0.1 | <a href='https://github.com/ilyasProgrammer'><img src='https://github.com/ilyasProgrammer.png' width='32' height='32' style='border-radius:50%;' alt='ilyasProgrammer'/></a> | Model Read Only
[module_analysis](module_analysis/) | 14.0.1.0.2 |  | Add analysis tools regarding installed modules to know which installed modules comes from Odoo Core, OCA, or are custom modules
[module_auto_update](module_auto_update/) | 14.0.1.1.1 |  | Automatically update Odoo modules
[module_change_auto_install](module_change_auto_install/) | 14.0.1.0.3 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Customize auto installables modules by configuration
[module_prototyper](module_prototyper/) | 14.0.1.0.1 |  | Prototype your module.
[nsca_client](nsca_client/) | 14.0.1.0.2 |  | Send passive alerts to monitor your Odoo application.
[onchange_helper](onchange_helper/) | 14.0.1.0.3 |  | Technical module that ease execution of onchange in Python code
[profiler](profiler/) | 14.0.1.0.0 | <a href='https://github.com/thomaspaulb'><img src='https://github.com/thomaspaulb.png' width='32' height='32' style='border-radius:50%;' alt='thomaspaulb'/></a> | profiler
[rpc_helper](rpc_helper/) | 14.0.1.2.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Helpers for disabling RPC calls
[scheduler_error_mailer](scheduler_error_mailer/) | 14.0.1.2.1 |  | Scheduler Error Mailer
[sentry](sentry/) | 14.0.3.0.2 | <a href='https://github.com/barsi'><img src='https://github.com/barsi.png' width='32' height='32' style='border-radius:50%;' alt='barsi'/></a> <a href='https://github.com/naglis'><img src='https://github.com/naglis.png' width='32' height='32' style='border-radius:50%;' alt='naglis'/></a> <a href='https://github.com/versada'><img src='https://github.com/versada.png' width='32' height='32' style='border-radius:50%;' alt='versada'/></a> <a href='https://github.com/moylop260'><img src='https://github.com/moylop260.png' width='32' height='32' style='border-radius:50%;' alt='moylop260'/></a> <a href='https://github.com/fernandahf'><img src='https://github.com/fernandahf.png' width='32' height='32' style='border-radius:50%;' alt='fernandahf'/></a> | Report Odoo errors to Sentry
[sequence_python](sequence_python/) | 14.0.1.0.0 |  | Calculate a sequence number from a Python expression
[session_db](session_db/) | 14.0.1.0.2 | <a href='https://github.com/sbidoul'><img src='https://github.com/sbidoul.png' width='32' height='32' style='border-radius:50%;' alt='sbidoul'/></a> | Store sessions in DB
[slow_statement_logger](slow_statement_logger/) | 14.0.1.0.1 |  | Log slow SQL statements
[sql_export](sql_export/) | 14.0.1.2.2 |  | Export data in csv file with SQL requests
[sql_export_excel](sql_export_excel/) | 14.0.1.1.1 |  | Allow to export a sql query to an excel file.
[sql_export_mail](sql_export_mail/) | 14.0.1.0.0 |  | Send csv file generated by sql query by mail.
[sql_request_abstract](sql_request_abstract/) | 14.0.1.3.0 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Abstract Model to manage SQL Requests
[test_base_time_window](test_base_time_window/) | 14.0.1.0.1 |  | Test Base model to handle time windows
[tracking_manager](tracking_manager/) | 14.0.1.3.0 | <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | This module tracks all fields of a model, including one2many and many2many ones.
[upgrade_analysis](upgrade_analysis/) | 14.0.3.0.0 |  | Performs a difference analysis between modules installed on two different Odoo instances
[url_attachment_search_fuzzy](url_attachment_search_fuzzy/) | 14.0.1.0.1 | <a href='https://github.com/mariadforgelow'><img src='https://github.com/mariadforgelow.png' width='32' height='32' style='border-radius:50%;' alt='mariadforgelow'/></a> | Fuzzy Search of URL in Attachments

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
