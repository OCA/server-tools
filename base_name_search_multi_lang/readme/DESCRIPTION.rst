This module extends the name search feature to use other translated language.

For example, if a product name in English is "Chair", and Thai is "เก้าอี้"

Given user language preference is English, when user type name to search
on product field, "Chair", the product with this name will be found.
But if user type in Thai, "เก้าอี้", no result will be shown.

With this module installed, and model product.product is set to use "Search Translated Name".
Search by Thai name, "เก้าอี้", now find the product "Chair".

Please also note that, this search feature is available only on Many2one field.
