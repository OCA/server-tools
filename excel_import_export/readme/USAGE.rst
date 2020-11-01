This module contain pre-defined function and wizards to make exporting, importing and reporting easy.

At the heart of this module, there are 2 `main methods`

- ``self.env['xlsx.export'].export_xlsx(...)``
- ``self.env['xlsx.import'].import_xlsx(...)``

For reporting, also call `export_xlsx(...)` but through following method

- ``self.env['xslx.report'].report_xlsx(...)``

After install this module, go to Settings > Excel Import/Export > XLSX Templates, this is where the key component located.

As this module provide tools, it is best to explain as use cases. For example use cases, please install **excel_import_export_sample**

**Use Case 1:** Export/Import Excel on existing document

This add export/import action menus in existing document (example - excel_import_export_sample/import_export_sale_order)

1. Create export action menu on document, <act_window> with res_model="export.xlsx.wizard" and src_model="<document_model>", and context['template_domain'] to locate the right template -- actions.xml
2. Create import action menu on document, <act_window> with res_model="import.xlsx.wizard" and src_model="<document_model>", and context['template_domain'] to locate the right template -- action.xml
3. Create/Design Excel Template File (.xlsx), in the template, name the underlining tab used for export/import -- <file>.xlsx
4. Create instruction dictionary for export/import in xlsx.template model -- templates.xml

**Use Case 2:** Import Excel Files

With menu wizard to create new documents (example - excel_import_export_sample/import_sale_orders)

1. Create report menu with search wizard, res_model="import.xlsx.wizard" and context['template_domain'] to locate the right template -- menu_action.xml
2. Create Excel Template File (.xlsx), in the template, name the underlining tab used for import -- <import file>.xlsx
3. Create instruction dictionary for import in xlsx.template model -- templates.xml

**Use Case 3:** Create Excel Report

This create report menu with criteria wizard. (example - excel_import_export_sample/report_sale_order)

1. Create report's menu, action, and add context['template_domain']  to locate the right template for this report -- <report>.xml
2. Create report's wizard for search criteria. The view inherits ``excel_import_export.xlsx_report_view`` and mode="primary". In this view, you only need to add criteria fields, the rest will reuse from interited view -- <report.xml>
3. Create report model as models.Transient, then define search criteria fields, and get reporing data into ``results`` field -- <report>.py
4. Create/Design Excel Template File (.xlsx), in the template, name the underlining tab used for report results -- <report_file>.xlsx
5. Create instruction dictionary for report in xlsx.template model -- templates.xml
