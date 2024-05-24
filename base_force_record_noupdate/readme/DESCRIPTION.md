This module adds a boolean field on models form view, allowing to force
`noupdate=True` to data linked to those models.

Upon setting the field to `True` on a given model, `noupdate=True` will
be set upon existing data linked to it. When creating new data linked to
that model, they will always have `noupdate=True` (unless the field is
reset on the model itself).
