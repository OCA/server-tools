The aim of the module is to provide a generic mixin for building url on record.

Natively odoo implementation of url is based on having an "id" in the url, this module
provide an alternative way of doing. Url are generated and stored in an uniq table (to ensure unicity).
Redirection are also managed.

This project was initial build for shopinvader as we need to have uniq url for the connected webshop.
But this concept can be reuse in other case and even replace the odoo url implementation.


