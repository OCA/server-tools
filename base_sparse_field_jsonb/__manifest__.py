{
    "name": "Base Sparse Field JSONB",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "Use PostgreSQL JSONB for sparse/serialized fields with GIN indexing",
    "author": "OBS Solutions B.V., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "LGPL-3",
    "depends": [
        "base_sparse_field",
    ],
    "data": [],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
}
