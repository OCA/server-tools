{
    "name" : "Management of Asymmetric Encryption Keys",
    "version" : "1.0",
    "author" : "Thomas Cook - Willow IT",
    "category" : "System",
    "description" : """
Asymmetric Encryption Keys 
==========================

Public key management and encryption that can be used for things such as storing credit card information securely. 

This is a generic module to depend on if you want to build something that required the use of public key encryption. 

Also contains a number of helper functions for common tasks such as credit card validation.

""",
    "website": "http://www.willowit.com.au",
    "images" : [],
    "depends" : [
    ],
    "data": [
        "ae_view.xml",
        "wizard/ae_activation_wizard_view.xml",
        "wizard/ae_pw_change_wizard_view.xml",
        "wizard/ae_password_prompt_wizard_view.xml",
        "security/ir.model.access.csv"
    ],
    "qweb" : [],
    "demo": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
