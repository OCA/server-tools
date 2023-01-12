This module depends on ``mail_environment`` in order to add "expiration dates"
per server.

Example of a configuration file (add those values to your server)::

  [incoming_mail.openerp_imap_mail1]
  cleanup_days = False  # default value
  purge_days = False  # default value
  cleanup_folder = NotParsed  # optional parameter
