To configure this module, you need to:

1.  Enable developer mode.
2.  Go to the form view of the model to which you want to add the new
    sequential default value.
3.  Hover over the field to which you want to add the sequential default
    value. A tooltip with more info will appear.
4.  Make sure the tooltip says *Type: char*. Only those fields will
    work.
5.  Take note of the *Object* and *Field*.
6.  Go to *Settings \> Technical \> Sequences & Identifiers \>
    Sequences*.
7.  Create one sequence with code named after this pattern:
    `base_sequence_default.{object}.fields.{field}`. E.g.:
    `base_sequence_default.res.partner.fields.name` to add a default
    sequenced name for new partners.
8.  Configure the sequence at will.
