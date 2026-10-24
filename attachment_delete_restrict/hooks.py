def post_init_hook(cr, registry):
    # Populate config parameters at the installation,
    # to avoid to raise CREATE SQL commands on ir_config_parameter
    # when users manipulate other configuration in res.config.settings model.
    # (The create can fail if user doesn't have create access on ir.config_parameter)
    # model
    cr.execute(
        """
    INSERT INTO ir_config_parameter (key, value)
    VALUES ('attachment_delete_restrict.global_delete_attachment_group_ids', '[]') ;
    INSERT INTO ir_config_parameter (key, value)
    VALUES ('attachment_delete_restrict.global_delete_attachment_user_ids', '[]') ;
    """
    )
