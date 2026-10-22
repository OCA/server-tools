def migrate(cr, version):
    """Field types mail cannot track are no longer trackable."""
    cr.execute(
        """
        UPDATE ir_model_fields
        SET trackable = FALSE, custom_tracking = FALSE
        WHERE ttype IN (
            'binary', 'json', 'many2one_reference',
            'properties_definition', 'reference'
        )
        """
    )
