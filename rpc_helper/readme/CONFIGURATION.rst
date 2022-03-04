Enable debug mode and go to "Technical -> Database Structure -> Models".

Open the model that you like to configure and go to the tab "RPC config".

There you see a text field which supports JSON configuration.

The configuration is the same you can pass via decorator.
The only difference is that you have to wrap values in a dictionary
like `{"disable": [...values...]}`.

To disable all calls::

    {
        "disable": ["all"],
    }

To disable only some methods::

    {
        "disable": ["create", "write", "another_method"],
    }

NOTE: on the resulting JSON will be automatically formatted on save for better readability.
