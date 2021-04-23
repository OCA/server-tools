To use this module, you need to:

* install the dependencies of your future module
* customize your instance by adding fields and creating inherited views
* create your menu items and their window actions
* prepare your data and demo data by creating filters
* create your own groups with access rights and record rules
* add your own access rights and record rules to an existing group

Once you have customized your instance properly, you can go to Settings > Module Prototypes > Prototypes
and create a new prototype:

* fill in the information of your module (enter the name, the description, the logo, etc.)
* in the Depencencies tab, select all the other modules that yours will be depending on
* in the Data & Demo tab, select your filters for data and demo data
* in the Fields tab, select the fields you created or customized
* in the Interface tab, select your menu items and your views
* in the Security tab, select your groups, access rights and record rules
* save and click on export

You will get a zip file containing your module ready to be installed and compliant with the
conventions of the OCA. You can then provide the module to a developer who have to implement
things like default values or onchange methods.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0
