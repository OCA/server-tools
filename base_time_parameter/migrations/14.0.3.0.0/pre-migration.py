from openupgradelib import openupgrade


def rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            (
                "base.time.parameter.version",
                "base_time_parameter_version",
                "value_text",
                "value",
            ),
        ],
    )


def type_text2float(cr):
    openupgrade.logged_query(
        cr, "UPDATE base_time_parameter SET type = 'float' WHERE type = 'text';"
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    rename_fields(env)
    type_text2float(cr)
