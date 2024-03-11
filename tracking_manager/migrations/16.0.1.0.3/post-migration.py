from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE ir_model_fields SET trackable = false;
        UPDATE ir_model_fields SET trackable = true
            WHERE name NOT IN (
                'activity_ids',
                'message_ids',
                'message_last_post',
                'message_main_attachment',
                'message_main_attachement_id'
            )
            AND store AND related IS NULL;
        """,
    )
