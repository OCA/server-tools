Go to *Settings > Technical > User Interface > Template Content Mappings* to
create/maintain records.

Following fields should be filled in:

* **Report** (optional): Report record that includes the string you'd like to replace.
  Setting a report record will automatically update the template field.
* **Template** (required): The main QWeb template (ir.ui.view record) that includes the
  string you'd like to replace.
* **Language** (optional): Target language for string replacement. If left blank, the
  replacement will be applied to all languages.
* **Content From** (required): An existing string to be replaced.
* **Content To** (optional): A new string to replace the existing string.
