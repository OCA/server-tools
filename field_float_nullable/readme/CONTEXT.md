In standard Odoo, `fields.Float` does not support distinguishing between `0.0` and `NULL` (i.e., an unset value).
By default, if a float field is left empty in the UI, it is stored as `0.0` in the database.
The goal is to allow users and developers to identify whether a float field has been filled in or not — something that cannot be reliably determined when `0.0` is used by default.
The module also integrates fully with Odoo’s UI (form views, list views, export, custom filters