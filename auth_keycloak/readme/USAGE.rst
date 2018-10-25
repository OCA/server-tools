Frontend
~~~~~~~~

When the provider is enabled you'll see an extra login button on login form.
Click on it to get redirected to Keycloak.

Backend
~~~~~~~

**Link existing users from Keycloak**

If you have existing users in Odoo and they are not linked to Keycloak yet
you can:

1. get back to Settings -> Users -> OAuth Providers -> Keycloak
2. configure "Users management" box
3. click on "Sync users" button
4. select the matching key
5. submit

Once the it's done all matching and updated users will be listed in a list view.
Now your users will be able to log in on Keycloak


**Push new users to Keycloak**

Usually Keycloak is already populated w/ your users base.
Many times this will come via LDAP, AD, pick yours.

Still, you might need to push some users to Keycloak on demand,
maybe just for testing.

If you need this, either you

1. go to a single user form
2. hit the button "Push to Keycloak" (in the header)
3. use the wizard to push it

or

1. go to the users list view
2. select some users
3. click on Actions -> Push to Keycloak
4. select "Keycloak" provider
5. push them all
