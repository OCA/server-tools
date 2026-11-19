A module implementing an import creates a log for the file it took in, splits
the file into units, and implements what importing one unit means.

Create the log with the file attached and the hash of its content:

    log = env["data.import.log"].create({
        "attachment_id": attachment.id,
        "content_hash": env["data.import.log"]._content_hash(content),
        "file_format": "csv",
        "encoding": "cp932",
    })

The same content may be logged more than once, as a sender may resend a file to
correct some of its units. Recognizing a unit that was already imported is up
to the module implementing the import; the hash is there to help it.

Schedule the parsing of the file:

    log._enqueue_parse()

The file is read in the same way whichever format it is in, split into units by
`_group_rows`, and one job is scheduled per unit. Every row is a unit by
default; override `_group_rows` to return `{key: rows}` when rows have to be
imported together. The rejected units are written back from the same grouping,
so do not split the file elsewhere.

Implement `_import_unit` on `data.import.log`. It is called once per unit, in
its own job and its own transaction:

- return an empty list when the unit is imported;
- return a list of values for `data.import.error` when the unit is rejected;
- raise `RetryableJobError` when the failure is transient and the unit should
  be attempted again.

Anything else raised is a crash: the transaction is rolled back and the unit is
reported as failed with its traceback.

Two hooks are called when the file is closed:

- `_finalize_file`, to dispose of the source file, extended by the module that
  knows where the file is stored;
- `_notify_outcome`, called when the import did not fully succeed, which posts
  a summary on the log by default.

Logs and their files are visible to the members of the Data Import Log group
and to administrators; add the users who follow the imports to that group.
