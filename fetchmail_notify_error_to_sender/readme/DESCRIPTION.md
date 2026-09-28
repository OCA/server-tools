If fetchmail is not able to correctly route an email, the email is
"silently" lost (you get an error message in server log).

For example, if you configure odoo mail system to route received emails
according to recipient address, it may happen users send emails to wrong
email address.

This module extends the functionality of fetchmail to allow you to
automatically send a notification email to sender, when odoo can't
correctly process the received email.
