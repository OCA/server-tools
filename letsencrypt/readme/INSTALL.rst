After installation, this module generates a private key for your account at
letsencrypt.org automatically in ``$data_dir/letsencrypt/account.key``. If you
want or need to use your own account key, replace the file.

For certificate requests to work, your site needs to be accessible via plain
HTTP, see below for configuration examples in case you force your clients to
the SSL version.

After installation, trigger the cronjob `Update letsencrypt certificates` and
watch your log for messages.
