Create a new module adding this one as a dependency, then add override method
``_get_field_names_to_skip_in_copy()`` in your models, adding the names of the fields
you don't want to have their translations copied.
