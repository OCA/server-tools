To use this module, you need to complete installation and configuration
parts.

Simply add the `X-Odoo-db=database1` header to your HTTP requests.
Please note that you need to delete the `session_id` cookie to take this
header into account otherwise odoo will retrieve it from your session.
