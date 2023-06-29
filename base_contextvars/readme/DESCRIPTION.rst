Patch Odoo threadlocals-based Environments to use contextvars instead. This is useful
when the Odoo ORM must be used together with asyncio code that may lead to the execution
spanning multiple threads.

This module must not be ported beyond 14.0.
