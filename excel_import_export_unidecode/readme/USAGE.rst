To apply unidecode just check the Unidecode field for the data where you want to apply it in the Excel template.
If you are defining the template you only have to specify @?unidecode? e.g. 'A2': 'picking_id.export_reference${value or ""}@?unidecode?'
