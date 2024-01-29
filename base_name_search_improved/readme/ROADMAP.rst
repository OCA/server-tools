* Also use fuzzy search, such as the Levenshtein distance:
  https://www.postgresql.org/docs/9.5/static/fuzzystrmatch.html
* The list of additional fields to search could benefit from caching, for efficiency.
* This feature could also be implemented for regular ``search`` on the ``name`` field.
* While adding m2o or other related field that also have an improved name search, that improved name search is not used (while if name_search is customizend on a module and you add a field of that model on another model it works ok). Esto por ejemplo es en productos si agregamos campo "categoría pública" y a categoría pública le ponemos "parent_id". Entonces vamos a ver que si buscamos por una categoría padre no busca nada, en vez si hacemos esa lógica en name_search de modulo si funciona
