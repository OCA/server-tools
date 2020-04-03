* Storing times using `float_time` widget requires extra processing to ensure
  computations are done in the right timezone, because the value is not stored
  as UTC in the database, and must therefore be related to a `tz` field.

  `float_time` in this sense should only be used for durations and not for a
  "point in time" as this is always needs a Date for a timezone conversion to
  be done properly. (Because a conversion from UTC to e.g. Europe/Brussels won't
  give the same result in winter or summer because of Daylight Saving Time).

  Therefore the right move would be to use a `resource.calendar` to define time
  windows using Datetime with recurrences.
