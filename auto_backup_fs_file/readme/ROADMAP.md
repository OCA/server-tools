- **Folder field behavior**: The `folder` field on the `db.backup` model specifies
  the backup storage directory. For records using the `fs_file` method, storage
  is controlled by the `fs_file` field's settings. As of v18.0, the `folder`
  field is hidden (`invisible`) and no longer required when `method='fs_file'`,
  so it no longer interferes with `fs_file` configurations. No auto-sync
  between both fields is performed since the methods are mutually exclusive.

- **Design limitation**: The current implementation has a design constraint due to
  `fs_storage` addon limitations. Since storage setting targets the
  `db.backup.fs.file` model, only one storage backend can effectively be used.
