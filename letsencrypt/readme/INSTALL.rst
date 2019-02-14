After installation, this module generates a private key for your account at
letsencrypt.org automatically in ``$data_dir/letsencrypt/account.key``. If you
want or need to use your own account key, replace the file.

For certificate requests to work, your site needs to be accessible via plain
HTTP, see below for configuration examples in case you force your clients to
the SSL version.

After installation, trigger the cronjob `Update letsencrypt certificates` and
watch your log for messages.

This addon depends on the ``openssl`` binary and the ``acme_tiny`` and ``IPy``
python modules.

For installing the OpenSSL binary you can use your distro package manager.
For Debian and Ubuntu, that would be:

    sudo apt-get install openssl

For installing the ACME-Tiny python module, use the PIP package manager:

    sudo pip install acme-tiny

For installing the IPy python module, use the PIP package manager:

    sudo pip install IPy
