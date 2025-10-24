This is the list of known issues for this module. Any proposal for
improvement will be very valuable.

- **Issue:**

  When using approve_sequence option in any tier.definition there can be
  inconsistencies in the systray notifications.

  **Description:**

  Field can_review in tier.review is used to filter out, in the systray
  notifications, the reviews a user can approve. This can_review field
  is updated **in the database** in method review_user_count, this can
  make it very inconsistent for databases with a lot of users and
  recurring updates that can change the expected behavior.

- **Migration to 15.0:**

  The parameter \_tier_validation_manual_config will become False, on
  14.0, the default value is True, as the change is applied after the
  migration. In order to use the new behavior we need to modify the
  value on our expected model.
