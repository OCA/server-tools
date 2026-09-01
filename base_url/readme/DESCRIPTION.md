The aim of this module is to provide a generic mixin for building urls on records.

The native odoo implementation of a record url is based on having an "id" in the url,
this module provides an alternative way of doing it.
Urls are generated and stored in an unique table (to ensure unicity).
Redirections are also managed in case of url changes.

This project was initial build for shopinvader as we need to have unique url for the connected webshop.
But this concept can be reused in other cases and even replace the odoo url implementation.
