This addon provides a ranked search method to get an ordered list of records
based on fuzzy matching of any number of fields.

The goal is to provide a simpler interface for finding a suitable record.

```python
    @api.model
    def ranked_search(self, fields_searches, threshold=0.5, limit=None, domain=None):
        """
        Perform a ranked search on the model using pg_trgm for fuzzy matching.
        :param fields_searches: {
            "field_name": {
                "value": <search_value>,
                "coefficient": <weight 0–100>
            },
            ...
        }
        :param threshold: minimum total score to return
        :param limit: maximum number of records
        :param domain: optional domain to filter records before scoring
        :return: dictionary with record IDs as keys and scores as values, ordered by relevance
        """
        ...
```
There are many cases where you actually want to perform not a domain search, but a ranked search on records.
For example, suppose that you have an integration with an external marketplace, with automatic order imports.
You get on an order some customer data. Suppose the customer data is as follows:
```json
{
  marketplace_id: int,
  name: str,
  address: dict,
  vat_number: int,
}
```

You may be fine with just creating a duplicate partner, and so this can be imported with the marketplace_id.
But, if the customer already bought, you may very much want to re-use an existing partner.
Of course, you can't match on the marketplace_id.
What you might want to do is something like:
```python
partner = self.env["res.partner"]
if customer_data["vat_number"]:
    domain = [("vat", "=", normalize(customer_data["vat_number"]))]
    partner = partner.search(domain, limit=1)
if not partner:
    street = customer_data["address"]["street"]
    domain = [("street", "ilike", street), ("name", "ilike", customer_data["name"])]
    partner = partner.search(domain, limit=1)
...
```

The point is that a match on the `vat_id` means we can re-use the same partner, and simply add a new address if necessary, since tax identifiers are unique (with some caveats handwaved by normalize).
If not, then matching on `name` is too lax; basically all countries tend to have some very generic name/surname combinations.
But matching on both name and address is very likely good enough.
There's another issue here: we should fuzzy match, as there may be differences due to specific systems.
For a very specific example, suppose the city name is `"'s-Hertogenbosch"`. Some systems could write it as `"s-Hertogenbosch"` as they can't handle the leading apostrophe.
Other systems might fill "missing" fields, such as addresses without street numbers (which used to be common in small villages).

Long story short: we want some fuzzy matching with a confidence score to match records from some json data to improve integrations.
Typically, it is good enough to take the best partner

The goal is not to remove all the conditionals that could come up in the example code above,
but greatly reduce it.

The goal of this module is to provide a standard way to do it.
Moreover, the lack of good fuzzy search mean that in some cases, the records should be all loaded in python
to perform the filtering/ordering/thresholding there, which has a dramatic impact on performance.
