This module extends the functionality of the database backup system in Odoo by introducing a new backup method: **Fs File**. This method allows storing database backups as files using an FSSPEC implementation.

## How to Use the Module

### 1. Configure the Backup Method
1. Navigate to **Settings** > **Technical** > **Database Structure** > **Automated Backups**.
2. Create or edit a backup configuration.
3. In the **Backup Method** field, select **Fs File**.
4. Configure other fields as needed, such as the backup format and retention settings.
5. Save the configuration.

### 2. Perform a Backup
1. From the list of backup configurations, select the one configured with the **Fs File** method.
2. Click the **Backup Now** button to initiate the backup process.
3. The backup will be stored as a file in the configured FSSPEC storage.

### 3. View Fs File Backups
1. Open the backup configuration form view.
2. In the top-right corner, you will see a **Backups** stat button (if backups exist).
3. Click the **Backups** button to view the list of Fs File backups associated with the configuration.

### 4. Manage Fs File Backups
- In the Fs File backups list view, you can see details such as the backup filename and associated database backup configuration.
- Use this view to manage or download backups as needed.

### 5. Cleanup and File Deletion

Backup retention is controlled by the **Days to Keep** field on the backup configuration. When this value is greater than 0, the automatic cleanup process removes expired backup records during each backup run.

When a backup record is deleted (either by automatic cleanup or manually from the list view), the physical backup file in the filesystem storage is **not removed immediately**. Instead, the file is marked for deferred deletion by the `fs_attachment` garbage collector (GC), which runs periodically via Odoo's autovacuum cron. Physical files are only removed from the storage backend once the GC confirms no database record references them.

This means:
- **Immediately after deletion**: the database record is gone, but the file may still exist in the storage backend for a short period.
- **After the next autovacuum cycle**: the file is permanently deleted from the storage backend.

This behavior requires the storage's `autovacuum_gc` flag to be enabled (the default). If disabled, files must be managed manually.

### Screenshots
- **Backup Configuration Form View**
  ![Backup Configuration Form](../static/description/db_backup_form_view.png)

- **Fs File Backups List View**
  ![Fs File Backups List](../static/description/db_backup_fs_file_tree_view.png)

### Notes
- Ensure that the FSSPEC storage is properly configured before using the **Fs File** method.
- This module adds a new stat button in the backup configuration form view to quickly access Fs File backups.

