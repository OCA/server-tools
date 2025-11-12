We wanted to be able to open a new quotation form (without creating it in the database) with default values coming from an external system using a GET route and redirect.

We couldn't find a way to pass our values to a new quotation form using Odoo standard.
That's why we created this module: it allows us to create a temporary action that we delete after it is used.
On this action, we add context that allows us to get the default values on the new quotation.
