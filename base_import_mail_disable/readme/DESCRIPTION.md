This module ensures that Odoo strictly disables outbound emails when importing massive quantities of data via the standard `base_import` wizard.

**Problems it solves:**
* Safeguards the external SMTP queue against badly-coded or third-party custom modules that might explicitly trigger `mail.mail.create` or `template.send_mail()` hooks during bulk imports.
* Dynamically intercepts outbound mail in the background and silently cancels the transmission sequence natively, guaranteeing 100% SMTP silence during data migrations.
