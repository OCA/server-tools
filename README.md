
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=19.0)
[![Pre-commit Status](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml/badge.svg?branch=19.0)](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml?query=branch%3A19.0)
[![Build Status](https://github.com/OCA/server-tools/actions/workflows/test.yml/badge.svg?branch=19.0)](https://github.com/OCA/server-tools/actions/workflows/test.yml?query=branch%3A19.0)
[![codecov](https://codecov.io/gh/OCA/server-tools/branch/19.0/graph/badge.svg)](https://codecov.io/gh/OCA/server-tools)
[![Translation Status](https://translation.odoo-community.org/widgets/server-tools-19-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/server-tools-19-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# server-tools

server-tools

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[auditlog](auditlog/) | 19.0.1.0.1 |  | Audit Log
[auto_backup](auto_backup/) | 19.0.1.0.1 |  | Backups database
[base_cron_exclusion](base_cron_exclusion/) | 19.0.1.0.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | Allow you to select scheduled actions that should not run simultaneously.
[base_exception](base_exception/) | 19.0.1.0.0 | <a href='https://github.com/hparfr'><img src='https://github.com/hparfr.png' width='32' height='32' style='border-radius:50%;' alt='hparfr'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_partition](base_partition/) | 19.0.1.0.0 |  | Base module that provide the partition method on all models
[base_search_fuzzy](base_search_fuzzy/) | 19.0.1.0.0 |  | Fuzzy search with the PostgreSQL trigram extension
[base_technical_user](base_technical_user/) | 19.0.1.0.0 |  | Add a technical user parameter on the company
[base_time_window](base_time_window/) | 19.0.1.0.0 |  | Base model to handle time windows
[base_view_inheritance_extension](base_view_inheritance_extension/) | 19.0.1.0.0 | <a href='https://github.com/hbrunn'><img src='https://github.com/hbrunn.png' width='32' height='32' style='border-radius:50%;' alt='hbrunn'/></a> | Adds more operators for view inheritance
[base_write_diff](base_write_diff/) | 19.0.1.0.0 |  | Prevents updates on fields whose values won't change anyway
[bus_alt_connection](bus_alt_connection/) | 19.0.1.0.0 |  | Needed when using PgBouncer as a connection pooler
[database_cleanup](database_cleanup/) | 19.0.1.0.3 |  | Database cleanup
[field_vector](field_vector/) | 19.0.1.0.0 | <a href='https://github.com/lmignon'><img src='https://github.com/lmignon.png' width='32' height='32' style='border-radius:50%;' alt='lmignon'/></a> | New specialized field to store vector data
[iap_alternative_provider](iap_alternative_provider/) | 19.0.1.0.0 | <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | Base module for providing alternative provider for iap apps
[module_auto_update](module_auto_update/) | 19.0.1.0.1 |  | Automatically update Odoo modules
[module_change_auto_install](module_change_auto_install/) | 19.0.1.0.0 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Customize auto installables modules by configuration
[onchange_helper](onchange_helper/) | 19.0.1.0.0 |  | Technical module that ease execution of onchange in Python code
[rpc_helper](rpc_helper/) | 19.0.1.0.0 | <a href='https://github.com/simahawk'><img src='https://github.com/simahawk.png' width='32' height='32' style='border-radius:50%;' alt='simahawk'/></a> | Helpers for disabling RPC calls
[scheduler_error_mailer](scheduler_error_mailer/) | 19.0.1.0.0 |  | Scheduler Error Mailer
[sentry](sentry/) | 19.0.1.0.0 | <a href='https://github.com/barsi'><img src='https://github.com/barsi.png' width='32' height='32' style='border-radius:50%;' alt='barsi'/></a> <a href='https://github.com/naglis'><img src='https://github.com/naglis.png' width='32' height='32' style='border-radius:50%;' alt='naglis'/></a> <a href='https://github.com/versada'><img src='https://github.com/versada.png' width='32' height='32' style='border-radius:50%;' alt='versada'/></a> <a href='https://github.com/moylop260'><img src='https://github.com/moylop260.png' width='32' height='32' style='border-radius:50%;' alt='moylop260'/></a> <a href='https://github.com/fernandahf'><img src='https://github.com/fernandahf.png' width='32' height='32' style='border-radius:50%;' alt='fernandahf'/></a> | Report Odoo errors to Sentry
[sequence_python](sequence_python/) | 19.0.1.0.0 |  | Calculate a sequence number from a Python expression
[session_db](session_db/) | 19.0.1.0.0 | <a href='https://github.com/sbidoul'><img src='https://github.com/sbidoul.png' width='32' height='32' style='border-radius:50%;' alt='sbidoul'/></a> | Store sessions in DB
[test_auditlog](test_auditlog/) | 19.0.1.0.0 |  | Additional unit tests for Audit Log based on accounting models
[tracking_manager](tracking_manager/) | 19.0.1.0.0 | <a href='https://github.com/Kev-Roche'><img src='https://github.com/Kev-Roche.png' width='32' height='32' style='border-radius:50%;' alt='Kev-Roche'/></a> <a href='https://github.com/sebastienbeau'><img src='https://github.com/sebastienbeau.png' width='32' height='32' style='border-radius:50%;' alt='sebastienbeau'/></a> | This module tracks all fields of a model, including one2many and many2many ones.
[tracking_manager_domain](tracking_manager_domain/) | 19.0.1.0.0 | <a href='https://github.com/CRogos'><img src='https://github.com/CRogos.png' width='32' height='32' style='border-radius:50%;' alt='CRogos'/></a> | This module extends the tracking manager to allow to define a domain on fields to track changes only when certain conditions apply.
[upgrade_analysis](upgrade_analysis/) | 19.0.1.1.2 | <a href='https://github.com/StefanRijnhart'><img src='https://github.com/StefanRijnhart.png' width='32' height='32' style='border-radius:50%;' alt='StefanRijnhart'/></a> <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Performs a difference analysis between modules installed on two different Odoo instances

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
