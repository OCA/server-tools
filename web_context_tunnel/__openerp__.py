{
    'name': 'Web Context Tunnel',
    'category': 'Hidden',
    'author': "Akretion,Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'description': """
Web Context Tunnel.
===================

The problem with OpenERP on_changes
-----------------------------------

OpenERP uses to pass on_change Ajax events arguments using positional
arguments. This is annoying as modules often need to pass extra arguments
that are not present in the base on_change signatures. As soon as two modules
try to alter this signature to add their extra arguments, they are incompatible
between them unless some extra glue module make them compatible again by
taking all extra arguments into account. But this leads to a combinatorial
explosion to make modules compatible again.

The solution
------------

This module provides a simple work around that will work in most of the cases.
In fact it works if the base on_change is designed to pass the context
argument. Else it won't work and you should go the old way. But in any case
it's a bad practice if an on_change doesn't pass the context argument and you
can certainly rant about these bad on_changes to the the context added in the
arguments.

So for an on_change passing the context, how does this module works?

Well OpenERP already has an elegant solution for an extension module to alter
an XML attributes: put an extension point in the view using
position="attributes" and then redefine the attribute. That is already used at
several places to replace the "context" attribute that the client will send to
the server.

The idea here is to wrap the extra arguments needed by your on_change inside
that context dictionary just as it were a regular Python kwargs. That context
should then be automatically propagated accross the on_change call chain,
no matter of the module order and without any need to hack any on_change
signature.

The issue with just position="attributes" and redefining the context, is that
again, if two independent modules redefine the context, they are incompatible
unless a third module accounts for both of them.

But with this module, an extension point can now use position="attributes" and
instead of redefining the "context" attribute, you will now just define a new
"context_foo" attribute this way:
<attribute name="context_foo">{'my_extra_field': my_extra_field}</attribute>.

This module modifies the web client in such a way that before sending the Ajax
on_change event request to the server, all the node attributes starting with
"context" are merged into a single context dictionnary, keeping the keys and
values from all extensions. In the rare case a module really wants to override
the value in context, then it needs to still override the original context
attribute (or the other original attribute).

And of course, if you should call your on_change by API or webservice instead
of using the web client, simply ensure you are wrapping the required extra
arguments in the context dictionary.

Tests
-----

This module comes with a simple test in static/test/context_tunnel.js.
To run it, open the page /web/tests?mod=web_context_tunnel in your browser
as explained here https://doc.openerp.com/trunk/web/testing
It should also be picked by the Python testing when testing with PhantomJS.

As for testing modules using web_context_tunnel with YAML, yes it's possible.
In fact you need to manually mimic the new web-client behavior by manually
ensuring you add the extra context keys you will need later in your on_change.
For instance, before the on_change is called, you can alter the context with
a !python statement like context.update({'my_extra_field': my_extra_field}).

You can see an example of module conversion to use web_context_tunnel here
for instance:
https://github.com/openerpbrasil/l10n_br_core/commit/33065366726a83dbc69b9f0031c81d82362fbfae
""",
    'version': '8.0.2.0.0',
    'depends': ['web'],
    'data': [
        'views/web_context_tunnel.xml',
    ],
    'test': [
        'static/test/context_tunnel.js',
    ],
    'css': [],
    'auto_install': False,
    'web_preload': False,
    "installable": False,
}
