* Also use fuzzy search, such as the Levenshtein distance:
  https://www.postgresql.org/docs/9.5/static/fuzzystrmatch.html
* The list of additional fields to search could benefit from caching, for efficiency.
* This feature could also be implemented for regular ``search`` on the ``name`` field.
* While adding m2o or other related field that also have an improved name
  search, that improved name search is not used (while if name_search is
  customizend on a module and you add a field of that model on another model it
  works ok). This happens for example in products if we add field "public category"
  and to public category we put "parent_id". Then we will see that if we search
  by a parent category it doesn't search anything, instead if we do that logic
  in name_search of module it works.
