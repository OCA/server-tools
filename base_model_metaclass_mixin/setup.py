import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name='base_model_metaclass_mixin',
    version='0.1',
    description=u"""This module handles methods to modify OpenERP base methods.
    It should be on the 'external_dependencies' key of your OpenERP module if
    you are going to use it.""",
    packages=find_packages(),
    install_requires=[
        'openerp',
    ]
)
