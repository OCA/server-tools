To use this module, you need to:

1. Go to *Settings > Technical > Sequences & Identifier > Manage Sequence Options*.
2. Based on extended module installed, different document types will be listed, i.e., Purchase Order.
3. Activite "Use sequence options" to use, if not, fall back to normal sequence.
4. For each option, provide,
    * Name: i.e., Customer Invoice for Cust A., Customer Payment, etc.
    * Apply On: a filter domain to test whether a document match this option.
    * Sequence: select underlining sequence to perform

**Note:**

* If no options matches the document, fall back to normal sequence.
* If there are multiple sequence options that match same document, error will be raised.
