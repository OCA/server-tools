import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            # server_environment_file does not exist as a packaged addon,
            # as it must be provided locally
            'server_environment_files': '',
        },
    },
)
