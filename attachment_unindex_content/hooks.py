def post_init_hook(env):
    """Clear the indexed data for records already in database"""
    env.cr.execute("UPDATE ir_attachment SET index_content=NULL")
