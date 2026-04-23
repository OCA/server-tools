This module extends Odoo's standard import wizard to allow identifying and updating
existing records by any combination of stored field values, without requiring the
External ID (`id`) column that changes across databases.

## Problem

In a standard Odoo import, updating an existing record requires including its **External
ID** (`id`) or its **Database ID** (`.id`). Both values change between instances
(production, staging, development, …), making it hard to prepare reusable import files.

## Solution

Configure one or more _match configurations_ that tell the module which field(s) to use
as a lookup key. At import time the module searches the database using those fields; if
a single matching record is found it is updated, otherwise a new record is created.

Multiple fields can be combined with AND semantics. Many2one fields are resolved
automatically by display name.
