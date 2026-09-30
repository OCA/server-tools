1. Create a GitHub user (e.g. a bot account) and add it as collaborator
   with write access to the target repository. Use a **private** repository:
   the reports contain user logins, IP addresses and data from tracebacks.
2. Log in as that user and create a personal access token (fine-grained:
   *Issues: Read and write* on the repository, or *Contents: Read and write*
   when sending files; classic: `repo` scope for private repositories).
3. Go to *Settings > Companies* and open the company.
4. Open the *Error Reports* tab.
5. Set the *GitHub Repository URL*, *GitHub User* and *GitHub Token*.
   Choose *Send As*: *Issue* creates one issue per error, *File in Repository*
   commits one Markdown file per error to
   `odoo_errors/<module>/<YYYY-MM-DD>/<HHMMSS>_<hash>.md`.
   Enable *Send Server Errors Automatically* to report an error as soon as
   the error dialog opens; otherwise errors are only reported when the user
   clicks the send button in the error dialog.
   Enable *Send by Email* and enter *Email Recipients* (comma-separated) to
   also send every report by email with the same subject and content. It is
   sent through the outgoing mail server; the sender is the company email.
   Email works without GitHub: leave the repository URL empty to only send
   emails.
6. *Skip Duplicate Errors* (disabled by default) reports an error with the
   same traceback only once per *Duplicate Period (Hours)* (24 by default;
   0 reports each error only once). Skipped occurrences are still counted.
7. Click *Test GitHub Connection* to check that GitHub is reachable and the
   token may create reports (nothing is created by the test). It warns when
   the repository is public.
8. Reload the browser so the new settings are loaded into the session.
9. Save the company, then click *Raise Dummy Server Error* on the company
   (or, in debug mode, open *Settings > Technical > Raise Dummy Server Error*)
   to trigger a real server error and use the send button in the error
   dialog.

Every reported error is listed in *Settings > Technical > Error Reports*
(debug mode), with its module, number of occurrences and the link to the
GitHub issue or file.
