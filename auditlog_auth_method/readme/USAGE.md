1.  Go to *Settings \> Technical \> Audit \> Rules* and open a rule.
2.  In **Authentication Methods**, check the methods to log. With none
    checked, every method is logged.
3.  Go to *Settings \> Technical \> Audit \> Logs* and filter or group the logs
    by **Authentication Method**.

*Settings \> Technical \> Audit \> Authentication Methods* lists what each
method covers.

The method describes how the request was authenticated, which can differ from
the user of the log, e.g. code run with `with_user()` or a queue job. The first
RPC call of a worker that has not loaded its registry yet is logged as *Server
side*.
