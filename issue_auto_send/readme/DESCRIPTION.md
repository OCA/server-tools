Adds a "Send to GitHub" button to the Odoo server error dialog.

When a server error with a traceback is shown to an internal user and a GitHub
repository is configured on the current company, the user can click
"Send to GitHub" to create an issue with the error report (title, message,
context details and traceback) in that repository. Only internal users can
send reports.

If *Send Server Errors Automatically* is enabled on the company, the report is
sent as soon as the error dialog opens and "Auto send active" is shown next
to the button. The dialog itself behaves exactly like the standard Odoo error
dialog.

The report is either created as a GitHub issue or committed as a Markdown file
to `odoo_errors/<module>/<YYYY-MM-DD>/<HHMMSS>_<hash>.md`. The module is the
Odoo addon that raised the error, taken from the innermost traceback frame
inside an addon (chained tracebacks are searched from the root cause, so
errors re-raised by e.g. server actions still point to the originating
module). It is also added to the report title as `[<module>]`. The hash
identifies the traceback, so repeated occurrences of the same error share it.

Repeated occurrences of the same error can be skipped for a configurable
period, so one broken screen seen by many users creates one report. All
occurrences are counted in an error report log.

Secrets are masked before sending: passwords, tokens, API keys, session ids
and cookies (as `key=value`, `key: value` or dictionary entries),
`Authorization` headers with `Bearer`/`Basic` credentials, credentials in URLs,
GitHub tokens and the configured GitHub token itself.

Optionally, the same report (same subject and content) is also sent by email
to a list of recipients through the outgoing mail server, with or without
GitHub.
