# Copyright 2025 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from lxml import etree

from odoo import SUPERUSER_ID, api
from odoo.tools.convert import xml_import
from odoo.tools.misc import file_path


def migrate(cr, version):
    """Reset email template because the previous version won't work in 18.0"""
    logger = logging.getLogger("odoo.addons.scheduler_error_mailer.migrations")
    env = api.Environment(cr, SUPERUSER_ID, {})
    external_id = "scheduler_error_mailer.scheduler_error_mailer"
    template = env.ref(external_id)

    # Using a snippet from template.reset.mixin's reset_template but only update body
    expr = "//*[local-name() = $tag and (@id = $xml_id or @id = $external_id)]"
    lang_false = {
        code: False for code, _ in env["res.lang"].get_installed() if code != "en_US"
    }
    module, xml_id = external_id.split(".")
    fullpath = file_path("scheduler_error_mailer/data/ir_cron_email_tpl.xml")
    template.update_field_translations("body_html", lang_false)
    doc = etree.parse(fullpath)
    for rec in doc.xpath(expr, tag="record", xml_id=xml_id, external_id=external_id):
        for node in rec.findall("field"):
            if node.attrib["name"] != "body_html":
                rec.remove(node)
        obj = xml_import(template.env, module, {}, mode="init", xml_filename=fullpath)
        obj._tag_record(rec)
        template._override_translation_term(module, [xml_id, external_id])

    logger.info(
        "Scheduler Error email template body was reset due to data model changes"
    )
