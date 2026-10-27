This module picks import files up from a filesystem storage and logs them.

A pick-up definition is a storage backend, the directories a file travels
through, the pattern the files are named by and the layout of their columns. A
scheduled scan lists the incoming directory, skips the files still being
written, creates one import log per file with the file attached, and holds the
file aside while it is imported, so that a later scan neither takes it again
nor overwrites it.

The file is released when its log closes. One that was read is filed as done
whatever became of its units, and the units that were rejected are written back
to the error directory on their own, for the sender to correct and resend. One
that could not be read is moved to the error directory whole. A file whose
earlier import succeeded in full is left where it is.

It relies on `data_import_log` for the log and on `fs_storage` for the
transport, which is any filesystem fsspec supports — sftp, S3, or a local
directory.
