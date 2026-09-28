A module implementing an import creates a log for the file it took in, splits
the file into units, and implements what importing one unit means.

Create the log with the file attached and the hash of its content:

    log = env["data.import.log"].create({
        "attachment_id": attachment.id,
        "content_hash": env["data.import.log"]._content_hash(content),
        "file_format": "csv",
        "encoding": "cp932",
    })

The hash is unique together with the file name, so a file offered twice by a
feed is refused rather than imported again.

Read the rows, in the same way whichever format the file is in, split them into
units, and schedule them:

    fieldnames, rows = log._read_rows()
    units = group_rows_somehow(rows)
    log._start_processing(len(units))
    for key, unit_rows in units.items():
        log._enqueue_unit(key, unit_rows)

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
