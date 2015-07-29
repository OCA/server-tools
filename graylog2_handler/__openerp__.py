{
    "name": "GrayLog2 Handler",
    "version": "0.0.1",
    "author": "Management and Accounting On-line",
    "website": "https://github.com/OCA/server-tools/",
    "summary": "Provides ability to send log messages to graylog2 server",
    "category": "Added functionality",
    "depends": [
        'base',
    ],
    "description": """
Aditional options available for config file:
    gelf_enabled: bool
    gelf_host: string, required if gelf_enabled=True
    gelf_port: integer, required if gelf_enabled=True
    gelf_localname: string

    """,
    "init_xml": [
    ],
    "demo": [
    ],
    "test": [
    ],
    "update_xml": [
    ],
    "active": True,
}
