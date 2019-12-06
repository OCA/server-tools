*This module is intended for developer only. It does nothing used alone.*

It helps to create `config.settings` by providing an abstract Class.

This class:

  * creates automatically related fields in 'res.config.settings'
    using those defined in 'res.company': it avoids duplicated field definitions.
  * company_id field with default value is created
  * onchange_company_id is defined to update all related fields
  * supported fields: char, text, integer, float, datetime, date, boolean, m2o
