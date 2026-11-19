This module matches the translated fields in all the installed
languages, in every search of the configured models: the search views,
the Many2one fields and any domain.

For example, if a product name in English is "Chair", and Thai is
"เก้าอี้", and model product.product is set to use "Translation Search",
typing "เก้าอี้" in the search box of the product list view, into the
Product field of a Sales Order, or searching with a domain such as
`[("name", "ilike", "เก้าอี้")]`, now finds the product "Chair".

Only the pattern operators (`like`, `ilike`, `=like`, `=ilike` and their
negations) are extended. With a negative operator, a record is excluded
as soon as one of its languages matches.
