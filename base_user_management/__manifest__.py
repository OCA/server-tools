{
    "name": "User Management",
    "summary": "Creates more subtle security group for managing users",
    "category": "Tools",
    "version": "16.0.1.0.0",
    "author": "Onestein,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "license": "AGPL-3",
    "depends": ["base", "auth_signup"],
    "data": [
        "security/res_groups.xml",
        "security/ir_model_access.xml",
        "security/ir_rule.xml",
        "menuitems.xml",
    ],
}
