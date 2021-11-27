Select the active companies from the web client widget, near the top right corner.
When doing so, the User's security Groups are recomputed, based on the Roles.

When the user changes the company selection, only the groups available to all active companies will be activated.

For example:

* A "SALES PERSON" and a "SALES MANAGER" roles are created.

* A user is assigned to the roles:
    * "SALES PERSON", with no specific company assigned (meaning all)
    * "SALES MANAGER" only to "My Company (Chicago)"

* When selecting active companies from the UI widget:
    * If only "My Company (San Francisco)" is active, "SALES PERSON" will be active.
    * If only "My Company (Chicago)" is active, "SALES PERSON" and "SALES MANAGER" will be active.
    * If both "My Company (San Francisco)" and "My Company (Chicago)" is active, "SALES PERSON" will be active.
