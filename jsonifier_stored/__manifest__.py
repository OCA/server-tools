# Copyright 2022 Camptocamp SA (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# @author Matthieu Méquignon <matthieu.mequignon@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "JSONify Stored",
    "summary": "Pre-compute and store JSON data on any model",
    "version": "14.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "maintainers": ["simahawk", "mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["jsonifier", "base_sparse_field", "queue_job"],
    "data": ["data/ir_cron.xml", "data/queue_job.xml"],
}
