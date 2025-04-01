1. **Review Documentation for Dependencies**
  Before configuring the module, ensure you have reviewed the documentation for the following modules:
  - `fs_attachment`
  - `fs_storage`
  These modules provide the necessary setup for file storage and attachment handling.

2. **Configure File Storage**
  - Navigate to **Settings** > **Technical** > **FS  Storage**.
  - Create or select an existing storage configuration.
  - Ensure the storage is properly set up and tested for accessibility.

3. **Link Backup File field to Storage**
  - While configuring the file storage in **Settings** > **Technical** > **FS Storage**, ensure that the `backup_file` from the `db.backup.fs.file` model is listed under the `Field` field.
  - This step is part of the storage configuration process.
  - Save the changes after verifying the setup.

  ![Example of File Storage Configuration](../images/file_storage_configuration.png)

4. **Verify Configuration**
  - Perform a test backup to ensure the files are being stored in the correct location.
  - Check the logs for any errors or warnings.

By following these steps, you will ensure that the module is properly configured for storing backups in the desired file storage system.
