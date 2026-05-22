- allows the use of specific operators into domain filters to search for similar vectors.
- dedicated widget to display the vector in a more user-friendly way.
- evaluate removing the psycopg2 adapter (register.py) in favor of explicit 
  casting in convert_to_column/convert_to_cache. Currently the adapter must be 
  registered before any SQL query reads vector columns, which creates a implicit 
  dependency on ir.model.fields._register_hook execution order. Without the adapter, 
  plain SQL queries would return raw strings instead of VectorValue objects.
