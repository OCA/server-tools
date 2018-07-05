* Also use fuzzy search, such as the Levenshtein distance:
  https://www.postgresql.org/docs/9.5/static/fuzzystrmatch.html
* The list of additional fields to search could benefit from caching, for efficiency.
* This feature could also be implemented for regular ``search`` on the ``name`` field.
