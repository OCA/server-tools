To use this module, the administrator can create different processors in
Settings > Technical > Import Processors. It offers 3 different kind of snippets
depending on the import stage:

1. Pre-Processor: This snippet is executed once after loading the file. This snippet is useful to set global variables or set configurations prior to the import of each entry

2. Processor: This snippet is executed on single entries or chunks of entries depending on the configuration.

3. Post-Processor: This snippet is executed after the entries are processed and can be used to clean up things in the database or log the processed data.

After configuration every user can use the processors `Favorites > Import Processor` on the specified models.
