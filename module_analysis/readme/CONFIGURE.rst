* Go to Apps / Module Analysis / Modules Types Rules

The Module types Rules are usefull to get the Type of a module, based on
it information.

This module comes with default rules.

    .. image:: ../static/description/default_module_type_rules.png


You can add your custom rules to identify the modules your team have
developped for exemple,

    .. image:: ../static/description/add_module_type_rules.png


to update the data manually, you have to :

* Go to 'Apps' / 'Update Apps List'

* Check the box 'Analyse Installed modules'

    .. image:: ../static/description/base_module_update.png

This will update analysis of your installed modules.

to update the data automatically, you have to :

* Go to 'Settings' / 'Technical' / 'Scheduled Actions'

* Configure the action 'Update Module Analysis'. (By default, the analysis will be done nightly)


Adding Extra data
~~~~~~~~~~~~~~~~~

If you want to analyse other data, (for exemple, having the number of HTML
files), create a custom modules and overload the module model :

.. code-block:: python

  from odoo import api, fields, models

  class IrModuleModule(models.Model):
     _inherit = 'ir.module.module'

     xml_documentation_qty = fields.Integer(
        string='Quantity of Comments in XML Files')

    @api.model
    def _get_analyse_settings(self):
        res = super()._get_analyse_settings()
        if not '.html' in res:
            res['.html'] = {}
        res['.html']['documentation'] 'xml_documentation_qty'
        return res

Exclude files and directories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two parameters are availaible in 'Settings' / 'Technical' / 'Parameters'
'System Parameters' :

    .. image:: ../static/description/config_parameters.png

The list of folders and filename will be exclude from the analysis.
You can change the default settings.
