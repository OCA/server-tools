from openupgradelib import openupgrade


def type_reference2record(cr):
    openupgrade.logged_query(
        cr, "UPDATE base_time_parameter SET type = 'record' WHERE type = 'reference';"
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    type_reference2record(cr)
