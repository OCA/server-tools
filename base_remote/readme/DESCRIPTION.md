This is a technical base module that keeps track of the remote clients
connecting to Odoo. For each request it resolves the client IP address to
a hostname when reverse DNS is available, and stores or updates a
``res.remote`` record with the hostname and the latest IP address.

Other modules can use these records to apply configuration, features or
access rules depending on the origin of the request. The records can be
reviewed in Settings / Remotes.
