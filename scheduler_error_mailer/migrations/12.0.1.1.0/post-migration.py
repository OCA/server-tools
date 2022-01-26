# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    template = env.ref("scheduler_error_mailer.scheduler_error_mailer")
    template.body_html = template.body_html.replace(
        "${ctx.get('job_exception') and ctx.get('job_exception').value",
        "${ctx.get('job_exception')",
    )
