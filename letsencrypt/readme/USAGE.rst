The module sets up a cronjob that requests and renews certificates automatically.

After the first run, you'll find a file called ``domain.crt`` in
``$datadir/letsencrypt``, configure your SSL proxy to use this file as certificate.
