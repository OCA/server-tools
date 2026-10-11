# Excel Import Required Fields

This module extends the OCA `excel_import_export` functionality to allow marking fields as **required** in XLSX import templates.

When a field is marked as required, the system checks the Excel file during import. If any required field is empty or missing, the import is stopped.

An error message is shown like:

```
Following fields are required to import
- Field Name 1
- Field Name 2
```

## Features

* Mark fields as required in XLSX templates
* Validate both header and row data
* Prevent import if required fields are missing
* Show clear error messages with field names
