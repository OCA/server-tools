from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        CREATE TABLE ir_model_group_readonly_rel_tmp AS TABLE ir_model_group_readonly_rel;
        """,
    )
