To use this module, you need to inherit the `abstract.url` model and override
the `_get_keyword_fields` method to include your custom url fields. By default,
the `_get_keyword_fields` method returns the record `name`.


Here is an example of how to override the `_get_keyword_fields` method to include the `default_code` field for `product.template` records:


```python

class ProductTemplate(models.Model):
    _inherit = ["product.template", "abstract.url"]
    _name = "product.template"

    def _get_keyword_fields(self):
        return super()._get_keyword_fields() + ["default_code"]

```

Your product template records will now have an `url_key` field that is generated from the `name` and `default_code` fields and a `redirect_url_key` field that will contain a list of redirect URLs (old `url_key` field values).
