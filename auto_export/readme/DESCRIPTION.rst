This addon brings configurable export templates able to filter on rows and to save the file to a selected path on the filesystem.
The new export templates are based on saved exports in Odoo (ir.exports) to select the columns the export.
An optional technical domain is used to filter on rows. The export is triggered in an asynchronous job as the selected user (default: Admin).

The following saving protocols are currently supported:
 - filesystem
