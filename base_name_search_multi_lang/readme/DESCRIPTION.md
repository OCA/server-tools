This module extends the name search feature to use other translated
languages.

For example, if a product name in English is "Chair", and Thai is "เก้าอี้"

Given user language preference is English, when user types name to search
on product field, "Chair", the product with this name will be found. But
if user types in Thai, "เก้าอี้", no result will be shown.

With this module installed, and model product.product is set to use
"Search Translated Name". Searching by Thai name, "เก้าอี้", now finds the
product "Chair".

Every search matching a translated field with a pattern is extended, so
this covers the Many2one fields as well as the search views.
