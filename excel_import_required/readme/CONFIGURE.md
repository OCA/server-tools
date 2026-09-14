This module (`excel_import_required`) extends the standard OCA `excel_import_export` functionality to allow administrators to enforce specific data fields as strictly required when importing datasets from Excel matrices.

If an Excel sheet is uploaded containing empty rows or blank cells for fields mapped as required, the system intercepts the database write and presents a consolidated `ValidationError` popup displaying all the missing parameters at once using their human-readable field labels.

---

## How to Configure

To flag an existing field map as **Required** directly from the system frontend:
1. Navigate to:
   **System Menus → Excel Import/Export → XLSX Templates**
2. Select your desired Template from the list view.
3. Open the template in **Form View**.
4. Go to the **Import** tab.
5. Locate the **Import Lines (`import_ids`)** section.
6. Find the column labeled **Required** (next to *Field Condition*).
7. Enable the **Required** checkbox for any field that must be mandatory
   (e.g., `Cell B4 → Field ref`).
8. Click **Save**.

---

## Validation Behavior

Once a field is marked as **Required**:

* During XLSX import, the system validates all required fields.
* If any required field contains:

  * Empty value
  * Blank cell
  * `False` / `None`

The import process will be **blocked**, and a validation warning will be displayed.

---

If required values are missing, the system raises the following error:

```
Following fields are required to import
- Field Name 1
- Field Name 2
- Field Name 3
```

* Validation applies only to fields marked as **Required**
* Validation is executed **before data is written to the database**

---
