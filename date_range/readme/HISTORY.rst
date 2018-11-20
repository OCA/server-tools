10.0.3.0.0 (2019-11-20)
~~~~~~~~~~~~~~~~~~~~~~~

* [IMP] Added hierarchical feature for date_range.
  (`#1380 <https://github.com/OCA/server-tools/pull/1380>`_)

10.0.2.0.1 (2018-11-19)
~~~~~~~~~~~~~~~~~~~~~~~

* [FIX] Fix bug in DateRange._onchange_company_id not called
  when type_id is changed
* [FIX] Fix bug in DateRangeType._check_company_id when called
  with more than one record. 
  (`#26 <https://github.com/OCA/server-ux/pull/26>`_)
* [IMP] Adapt module to work in multi company.
  (`#10 <https://github.com/OCA/server-ux/pull/10>`_)
* [FIX] Fix unlink date range type. 
  (`#9 <https://github.com/OCA/server-ux/pull/9>`_)
