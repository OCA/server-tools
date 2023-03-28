To configure this module, you need to:

#. Enable developer mode.
#. Go to the form view of the model to which you want to add the new sequential default value.
#. Hover over the field to which you want to add the sequential default value. A tooltip with more info will appear.
#. Make sure the tooltip says *Type: char*. Only those fields will work.
#. Take note of the *Object* and *Field*.
#. Go to *Settings > Technical > Sequences & Identifiers > Sequences*.
#. Create one sequence with code named after this pattern:
   ``base_sequence_default.{object}.fields.{field}``.
   E.g.: ``base_sequence_default.res.partner.fields.name`` to add a default
   sequenced name for new partners.
#. Configure the sequence at will.
