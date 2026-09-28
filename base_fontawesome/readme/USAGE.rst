Now, all free icons from `Font Awesome <https://fontawesome.com/icons?d=gallery&m=free>`_
can be used on odoo. It also adds three options in order to add the icons:
* solid_icon
* regular_icon
* brand_icon
The usage depends on the configuration of the icon.

For example, brand_icon is necessary if we are using an icon of a brand::

    <button brand_icon="fa-amazon-pay" string=" fa-amazon-pay"/>

    <button brand_icon="fas fa-hand-sparkles" string=" fas fa-hand-sparkles"/>

    <button brand_icon="fas fa-handshake-slash" string=" fas fa-handshake-slash"/>

Icon picker widget
~~~~~~~~~~~~~~~~~~~

This module also provides a reusable ``fontawesome_picker`` field widget. Apply it
to any ``Char`` field that stores a FontAwesome CSS class to get a searchable grid
of the icons currently loaded, with a live preview, instead of typing the class by
hand::

    <field name="icon" widget="fontawesome_picker"/>

Selecting an icon writes its full class (for example ``fa fa-shopping-cart``) into
the field. The catalog is read at runtime from the loaded ``v4-shims`` stylesheet,
i.e. the icons that render with the standard ``fa fa-x`` class regardless of their
style (solid, regular or brand) and of the assets bundle they are shown in. The
widget is meant for form views.
