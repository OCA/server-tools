
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=11.0)
[![Pre-commit Status](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml/badge.svg?branch=11.0)](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml?query=branch%3A11.0)
[![Build Status](https://github.com/OCA/server-tools/actions/workflows/test.yml/badge.svg?branch=11.0)](https://github.com/OCA/server-tools/actions/workflows/test.yml?query=branch%3A11.0)
[![codecov](https://codecov.io/gh/OCA/server-tools/branch/11.0/graph/badge.svg)](https://codecov.io/gh/OCA/server-tools)
[![Translation Status](https://translation.odoo-community.org/widgets/server-tools-11-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/server-tools-11-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Tools for server environment(s)

Tools for Odoo Administrators to improve some technical features on Odoo.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[attachment_base_synchronize](attachment_base_synchronize/) | 11.0.1.0.0 |  | This module enhances ir.attachment for better control of import and export of files
[attachment_unindex_content](attachment_unindex_content/) | 11.0.1.0.0 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![ebirbe](https://github.com/ebirbe.png?size=30px)](https://github.com/ebirbe) | Disable indexing of attachments
[auditlog](auditlog/) | 11.0.1.0.1 |  | Audit Log
[auto_backup](auto_backup/) | 11.0.1.2.0 |  | Backups database
[base_cron_exclusion](base_cron_exclusion/) | 11.0.1.0.0 |  | Allow you to select scheduled actions that should not run simultaneously.
[base_cron_oneshot](base_cron_oneshot/) | 11.0.1.0.0 |  | Allows creating of single-use disposable crons.
[base_directory_file_download](base_directory_file_download/) | 11.0.1.0.0 |  | Download all files of a directory on server
[base_exception](base_exception/) | 11.0.1.1.2 |  | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_fontawesome](base_fontawesome/) | 11.0.5.7.1 |  | Up to date Fontawesome resources.
[base_name_search_improved](base_name_search_improved/) | 11.0.1.0.1 |  | Friendlier search when typing in relation fields
[base_remote](base_remote/) | 11.0.1.0.4 |  | Remote Base
[base_search_fuzzy](base_search_fuzzy/) | 11.0.1.0.0 |  | Fuzzy search with the PostgreSQL trigram extension
[base_technical_user](base_technical_user/) | 11.0.1.0.0 |  | Add a technical user parameter on the company
[base_view_inheritance_extension](base_view_inheritance_extension/) | 11.0.1.0.0 |  | Adds more operators for view inheritance
[company_country](company_country/) | 11.0.1.0.0 | [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![luisg123v](https://github.com/luisg123v.png?size=30px)](https://github.com/luisg123v) | Set country to main company
[configuration_helper](configuration_helper/) | 11.0.1.0.0 |  | Configuration Helper
[database_cleanup](database_cleanup/) | 11.0.1.0.0 |  | Database cleanup
[datetime_formatter](datetime_formatter/) | 11.0.1.0.0 |  | Helper functions to give correct format to date[time] fields
[dbfilter_from_header](dbfilter_from_header/) | 11.0.1.0.0 |  | Filter databases with HTTP headers
[dead_mans_switch_client](dead_mans_switch_client/) | 11.0.1.0.0 |  | Be notified when customers' Odoo instances go down
[fetchmail_incoming_log](fetchmail_incoming_log/) | 11.0.1.0.0 |  | Log all messages received, before they start to be processed.
[fetchmail_notify_error_to_sender](fetchmail_notify_error_to_sender/) | 11.0.1.0.0 |  | If fetching mails gives error, send an email to sender
[fields_relation_data](fields_relation_data/) | 11.0.1.0.0 |  | Show relations data in ir.model.fields tree views
[html_image_url_extractor](html_image_url_extractor/) | 11.0.1.0.0 |  | Extract images found in any HTML field
[html_text](html_text/) | 11.0.1.0.2 |  | Generate excerpts from any HTML field
[letsencrypt](letsencrypt/) | 11.0.2.0.0 |  | Request SSL certificates from letsencrypt.org
[mail_cleanup](mail_cleanup/) | 11.0.1.0.0 |  | Mark as read or delete mails after a set time
[mail_template_attachment_i18n](mail_template_attachment_i18n/) | 11.0.1.0.0 |  | Set language specific attachments on mail templates.
[module_auto_update](module_auto_update/) | 11.0.2.0.4 | [![sbidoul](https://github.com/sbidoul.png?size=30px)](https://github.com/sbidoul) | Automatically update Odoo modules
[nsca_client](nsca_client/) | 11.0.1.0.0 |  | Send passive alerts to monitor your Odoo application.
[onchange_helper](onchange_helper/) | 11.0.1.0.0 |  | Technical module that ease execution of onchange in Python code
[profiler](profiler/) | 11.0.2.0.0 |  | profiler
[record_archiver](record_archiver/) | 11.0.1.0.0 |  | Records Archiver
[resource_calendar_schedule_iteration](resource_calendar_schedule_iteration/) | 11.0.1.0.0 |  | Resource Calendar Schedule Iteration
[scheduler_error_mailer](scheduler_error_mailer/) | 11.0.1.0.0 |  | Scheduler Error Mailer
[sentry](sentry/) | 11.0.1.1.0 |  | Report Odoo errors to Sentry
[sql_request_abstract](sql_request_abstract/) | 11.0.1.0.1 |  | Abstract Model to manage SQL Requests
[test_configuration_helper](test_configuration_helper/) | 11.0.1.0.0 |  | Configuration Helper - Tests
[test_mail_template_attachment_i18n](test_mail_template_attachment_i18n/) | 11.0.1.0.0 |  | Test suite for mail_template_attachment_i18n.
[users_ldap_groups](users_ldap_groups/) | 11.0.1.0.0 |  | Adds user accounts to groups based on rules defined by the administrator.

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
