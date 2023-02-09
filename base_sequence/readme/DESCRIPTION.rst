This module refactor the `ir.sequence` allowing more legends to be added with minimal code duplication and
adding `preview` fields on both `ir.sequence` and `ir.sequence.date_range` models.
the `preview` field is a computed fields that only visible in edit-mode of the form view works with `range_` and `range_end_`.
It helps users to check and validate the prefix, suffix, and padding configuration easily without a need to actually generate an actual document.

Adding more legends to `ir.sequence` requires an extension of an inner method `_interpolation_dict()`
of the `_get_prefix_suffix()` method. An extension of an inner method is impractical,
therefore this module override the `_get_prefix_suffix()` method
by moving the inner private method `_interpolation_dict()` to a private method.
Therefore, this allows another module to add more legends to the `ir.sequence`.

This modules works as a base module to other modules to add more legends to `ir.sequence`.
and extends the `ir.sequence` allowing `range_end_` , `range_period_` and `qoy` legends. It adds the following legends:

* The end of `date_range` year with century: `%(range_end_year)s`
* The end of `date_range` year without century: `%(range_end_y)s`
* The end of `date_range` month: `%(range_end_month)s`
* The end of `date_range` day: `%(range_end_day)s`
* The end of `date_range` day of the year: `%(range_end_doy)s`
* The end of `date_range` week of the year: `%(range_end_woy)s`
* The end of `date_range` weekday: `%(range_end_weekday)s`
* The end of `date_range` hour in 24-hour: `%(range_end_h24)s`
* The end of `date_range` hour in 12-hour: `%(range_end_h12)s`
* The end of `date_range` minute: `%(range_end_min)s`
* The end of `date_range` second: `%(range_end_sec)s`
* The period of `date_range` month: `%(range_period_month)s`
* Quarter of the Year: `%(qoy)s`
* The begin of `date_range` quarter of the Year: `%(range_qoy)s`
* The end of `date_range` quarter of the Year: `%(range_end_qoy)s`
