1. Go to **Settings → Import → Import Match Configurations**.
2. Create a new configuration:

   - **Name** – a free label (e.g. `E-commerce categories by name + seo_name`).
   - **Model** – the Odoo model to target (e.g. `product.public.category`).
   - **Match Fields** – one or more stored fields to match on (e.g. `name` and
     `seo_name`).

3. Save the configuration.

Multiple configurations can exist for the same model. The **Priority** (sequence) field
controls which is tried first; the first one that returns a unique match is applied.
