
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/server-tools/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/server-tools/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/server-tools/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/server-tools/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/server-tools)
[![Translation Status](https://translation.odoo-community.org/widgets/server-tools-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/server-tools-17-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Server Tools

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[auditlog](auditlog/) | 17.0.1.0.0 |  | Audit Log
[base_cron_exclusion](base_cron_exclusion/) | 17.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) [![ChrisOForgeFlow](https://github.com/ChrisOForgeFlow.png?size=30px)](https://github.com/ChrisOForgeFlow) | Allow you to select scheduled actions that should not run simultaneously.
[base_exception](base_exception/) | 17.0.1.0.1 | [![hparfr](https://github.com/hparfr.png?size=30px)](https://github.com/hparfr) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | This module provide an abstract model to manage customizable exceptions to be applied on different models (sale order, invoice, ...)
[base_partition](base_partition/) | 17.0.1.0.0 |  | Base module that provide the partition method on all models
[base_technical_user](base_technical_user/) | 17.0.1.0.0 |  | Add a technical user parameter on the company
[base_view_inheritance_extension](base_view_inheritance_extension/) | 17.0.1.0.1 |  | Adds more operators for view inheritance
[database_cleanup](database_cleanup/) | 17.0.1.2.1 |  | Database cleanup
[dbfilter_from_header](dbfilter_from_header/) | 17.0.1.0.0 |  | Filter databases with HTTP headers
[iap_alternative_provider](iap_alternative_provider/) | 17.0.1.0.0 | [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | Base module for providing alternative provider for iap apps
[jsonifier](jsonifier/) | 17.0.1.0.0 |  | JSON-ify data for all models
[module_analysis](module_analysis/) | 17.0.1.0.1 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Add analysis tools regarding installed modules to know which installed modules comes from Odoo Core, OCA, or are custom modules
[module_auto_update](module_auto_update/) | 17.0.1.0.0 |  | Automatically update Odoo modules
[module_change_auto_install](module_change_auto_install/) | 17.0.1.0.2 | [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Customize auto installables modules by configuration
[onchange_helper](onchange_helper/) | 17.0.1.0.1 |  | Technical module that ease execution of onchange in Python code
[scheduler_error_mailer](scheduler_error_mailer/) | 17.0.1.0.0 |  | Scheduler Error Mailer
[sentry](sentry/) | 17.0.1.0.0 | [![barsi](https://github.com/barsi.png?size=30px)](https://github.com/barsi) [![naglis](https://github.com/naglis.png?size=30px)](https://github.com/naglis) [![versada](https://github.com/versada.png?size=30px)](https://github.com/versada) [![moylop260](https://github.com/moylop260.png?size=30px)](https://github.com/moylop260) [![fernandahf](https://github.com/fernandahf.png?size=30px)](https://github.com/fernandahf) | Report Odoo errors to Sentry
[server_action_logging](server_action_logging/) | 17.0.1.0.0 |  | Module that provides a logging mechanism for server actions
[session_db](session_db/) | 17.0.1.0.0 | [![sbidoul](https://github.com/sbidoul.png?size=30px)](https://github.com/sbidoul) | Store sessions in DB
[tracking_manager](tracking_manager/) | 17.0.1.0.6 | [![Kev-Roche](https://github.com/Kev-Roche.png?size=30px)](https://github.com/Kev-Roche) [![sebastienbeau](https://github.com/sebastienbeau.png?size=30px)](https://github.com/sebastienbeau) | This module tracks all fields of a model, including one2many and many2many ones.
[upgrade_analysis](upgrade_analysis/) | 17.0.1.0.0 | [![StefanRijnhart](https://github.com/StefanRijnhart.png?size=30px)](https://github.com/StefanRijnhart) [![legalsylvain](https://github.com/legalsylvain.png?size=30px)](https://github.com/legalsylvain) | Performs a difference analysis between modules installed on two different Odoo instances


Unported addons
---------------
addon | version | maintainers | summary
--- | --- | --- | ---
[views_migration_17](views_migration_17/) | 17.0.1.0.0 (unported) |  | Views Migration to v17

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
