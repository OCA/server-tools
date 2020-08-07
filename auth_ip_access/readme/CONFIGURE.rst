Go to menu *Settings -> Technical -> Security -> IP Access Rules* to create
access rules for the group whose access you want to limit. If no rules exist
for the groups of a user, it is not restricted to login from anywhere.

Each rule allows you to allow access for a specific group, or user, from IP
address or an IP network (using a netmask, e.g. 192.168.0.1/24).

Rules can be configured for a group, or for a user but not for both at the
same time. If neither group or user is configured, the rule is applied
globally.

A special case is where you allow logins from *any* private network (e.g.
networks in the 192.168.x.x or the 10.x.x.x ranges). You can create such a
rule by ticking the *private* checkbox on the rule.

If you accidentally lock yourself out you can regain access by accessing
your Odoo database through SQL and execute the following command.

.. code-block:: SQL

   UPDATE ip_access_rule SET active = FALSE;

You will need to restart Odoo to clear the IP access cache. This will lift all IP access restrictions.

Note: if you run Odoo behind a proxy (and you should, because where do you get your
SSL encryption from?), you need to set *proxy_mode = True* in the Odoo
configuration file to ensure that the remote address is properly propaged to
Odoo and is not set to the IP address of the proxy server. A setup like this
is dependent on the proxy server setting the correct remote address in the
*X-Forwarded-For* header.
