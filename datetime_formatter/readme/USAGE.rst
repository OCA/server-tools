This module adds a technical programming feature, and it should be used by
addon developers, not by end users. This means that you must not expect to see
any changes if you are a user and install this, but if you find you have it
already installed, it's probably because you have another modules that depend
on this one.

If you are a developer, to use this module, you need to:

* Call anywhere in your code::

    formatted_string = self.env["res.lang"].datetime_formatter(datetime_value)

* If you use Qweb::

    <t t-esc="env['res.lang'].datetime_formatter(datetime_value)"/>

* If you call it from a record that has a `lang` field::

    formatted_string = record.lang.datetime_formatter(record.datetime_field)

* ``models.ResLang.datetime_formatter`` docstring explains its usage.
