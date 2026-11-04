# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import SUPERUSER_ID, api

RULES = (
    "base_time_parameter.base_time_parameter_multi_company_rule",
    "base_time_parameter.base_time_parameter_version_multi_company_rule",
)
OLD_DOMAIN = "[('company_id', 'in', company_ids)]"
NEW_DOMAIN = "['|', ('company_id', '=', False), ('company_id', 'in', company_ids)]"


def _normalize(domain):
    return "".join((domain or "").split()).replace('"', "'")


def migrate(cr, version):
    """Let the multi-company rules show the parameters with no company.

    The rules are `noupdate` data, so an upgrade leaves the domain of an
    existing database alone. Rewrite it, but only where it still is the one
    this module shipped: a rule somebody edited is theirs.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in RULES:
        rule = env.ref(xmlid, raise_if_not_found=False)
        if rule and _normalize(rule.domain_force) == _normalize(OLD_DOMAIN):
            rule.domain_force = NEW_DOMAIN
