# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_model_renames = [
    ("openupgrade.analysis.wizard", "upgrade.analysis"),
    ("openupgrade.attribute", "upgrade.attribute"),
    ("openupgrade.comparison.config", "upgrade.comparison.config"),
    ("openupgrade.record", "upgrade.record"),
    ("openupgrade.generate.records.wizard", "upgrade.generate.record.wizard"),
    ("openupgrade.install.all.wizard", "upgrade.install.wizard"),
]

_table_renames = [
    ("openupgrade_analysis_wizard", "upgrade_analysis"),
    ("openupgrade_attribute", "upgrade_attribute"),
    ("openupgrade_comparison_config", "upgrade_comparison_config"),
    ("openupgrade_record", "upgrade_record"),
    ("openupgrade_generate_records_wizard", "upgrade_generate_record_wizard"),
    ("openupgrade_install_all_wizard", "upgrade_install_wizard"),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
