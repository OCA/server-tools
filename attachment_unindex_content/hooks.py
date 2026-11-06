def post_init_hook(cr, registry):
    """Clear the indexed data for records already in database"""
    cr.execute(
        "UPDATE ir_attachment SET index_content=NULL WHERE index_content IS NOT NULL"
    )
