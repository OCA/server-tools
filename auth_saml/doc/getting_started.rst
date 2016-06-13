Getting started with Authentic2
===============================

This is quick howto to help setup a service provider that will be able
to use the IDP from Authentic2

We will mostly cover how to setup your rsa keys and certificates


Creating the certs
------------------

Use easy-rsa from the easy-rsa package (or from the openvpn project)

Example script below with comment saying what you should do between each
command::

    #clean your vars

    source ./vars

    ./build-dh
    ./pkitool --initca

    #change your vars to math a new client cert

    source ./vars

    ./pkitool myclient


Congratulations, you now have a client certificate signed by a shiny new
CA under you own private control.

Configuring authentic
---------------------

We will not describe how to compile requirements nor start an authentic server.

Just log into your authentic admin panel::

  https://myauthenticserver/admin


and create a new "liberty provider".

You'll need to create a metadata xml file from a template (TODO)

You'll need to make sure it is activated and that the default protocol rules
are applied (ie: the requests are signed and signatures are verified)

Configuring OpenERP
-------------------

After installing the auth_saml module you should have new configuration
options in the admin panel.

You'll see a demonstration setup that points to a localhost:8000
identity provider (IDP).

DO NOT USE THIS PROVIDER!!! This is a demonstration only setup and contains
a private key that everyone can see in the source code of this module...

Using a private key when it has been compromised (ie: shared with the world)
is a really bad idea for an authentication system.

I'll say it again just to make sure you understand::

  DO NOT USE THE DEMONSTRATION CONFIGURATION AND KEYS
  IN ANY SERVER OTHER THAN A DEMO LOCALHOST MACHINE FOR
  TESTING PURPOSES.

  DOING SO WILL SURELY LEAD TO YOUR IDENTIY BEING STOLEN, YOUR SERVERS
  BEING ROOTED AND MORE SERIOUSLY TO THE END OF THE WORLD AND OTHER
  SUCH CALAMITIES YOU DON'T WANT TO EXPERIENCE TOO EARLY...

Seriously I hope you got the message loud and clear... Don't do that.
Follow the creating certs guide just above.

Copy the metadata from your identity provider::

  wget https://myauthenticserver/idp/saml2/metadata

and make sure the URLs point where they should. Edit the file if necessary.

Then save its content into the corresponding box in the openerp SAML2 Provider form.

There are additional SAML-related settings in Configuration > General settings.
