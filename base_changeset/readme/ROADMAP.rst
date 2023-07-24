* Only a subset of the type of fields is actually supported
* Multicompany not fully supported
* The popover widget indicating the number of pending changes is not shown for
  fields without a label at the moment. The approach was already failing in 15.0
  (in the case of inline fields such as the partner address fields)
  and even in 14.0 (in the case of fields for which no value was set yet).
