# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    template = env.ref("scheduler_error_mailer.scheduler_error_mailer")
    template.body_html = template.body_html.replace(
        "${object.model or ''}", "${object.model_id.name or ''}"
    )
    template.body_html = template.body_html.replace(
        "<li>Method : ${object.function or ''}</li>", ""
    )
    template.body_html = template.body_html.replace(
        "<li>Arguments : ${object.args or ''}</li>",
        "<li>Python code : <code>${object.code or ''}</code></li>",
    )
