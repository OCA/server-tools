{
    "name": "Store Audit Log in Clickhouse",
    "version": "18.0.1.0.0",
    "summary": "Asynchronous audit log storage in ClickHouse",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA), Cetmix",
    "website": "https://github.com/OCA/server-tools",
    "depends": [
        "auditlog",
        "queue_job",
    ],
    "external_dependencies": {
        "python": ["clickhouse-driver"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/auditlog_clickhouse_queue.xml",
        "views/auditlog_clickhouse_config_views.xml",
    ],
}
