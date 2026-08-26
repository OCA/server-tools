* Custom properties cannot be shared among templates.
* Required attributes are for now only set in the UI, not in the ORM itself.
* Support recursive templates using options

  .. figure:: /base_custom_info/static/description/customizations-everywhere.jpg
     :alt: Customizations Everywhere

  If you assign an *additional template* to an option, and while using the owner
  form you choose that option, you can then press *reload custom information
  templates* to make the owner update itself to include all the properties in all
  the involved templates. If you do not press the button, anyway the reloading
  will be performed when saving the owner record.

  .. figure:: /base_custom_info/static/description/templateception.jpg
     :alt: Templateception

  I.e., if you select the option "Needs videogames" for the property "What
  weaknesses does he/she have?" of a smart partner and press *reload custom
  information templates*, you will get 2 new properties to fill: "Favourite
  videogames genre" and "Favourite videogame".
