**Creating an Export Schema:**

1. Navigate to **JSON Export Engine > Configuration > Export Schemas**.
2. Create a new schema:
   - Select the target model (e.g., ``res.partner``, ``product.product``)
   - Click **Select Fields to Export** to interactively choose fields
     (including nested relational fields)
   - Optionally set a domain filter to limit which records are exported
   - Configure options: record limit, whether to include the record ID,
     and preview count
3. Click **Refresh Preview** to see sample JSON output.
4. Check the **JSON Schema** tab to see the auto-generated JSON Schema (draft-07)
   describing the structure of the exported data.

**REST Endpoints:**

1. In the schema form, go to the **Endpoints** tab.
2. Add an endpoint with a route path (e.g., ``partners``).
3. Choose authentication type:

   - **API Key**: A key is auto-generated when you select this option.
     Use the copy button to grab it. Pass via the ``X-API-Key`` HTTP header.
   - **Session (Logged-in User)**: Uses Odoo's session cookie.
   - **No Authentication**: Open access (use with caution).

4. Two URLs are generated for each endpoint:

   - **Data URL**: ``https://your-odoo.com/api/json_export/partners``
     returns JSON data
   - **Schema URL**: ``https://your-odoo.com/api/json_export/partners/schema``
     returns the full API response schema (JSON Schema draft-07)

5. **Pagination** is controlled from the endpoint settings:

   - Enable **Paginate** and set **Page Size** to split results into pages.
     Navigate with ``?page=2`` or ``?page=last``.
   - Disable **Paginate** to return all records in a single response.
   - The response includes navigation links (``first``, ``last``,
     ``next``, ``prev``) when pagination is enabled.

6. Example call with API key:

   ```
   curl -H "X-API-Key: <your-key>" https://your-odoo.com/api/json_export/partners
   ```

**Webhooks:**

1. In the schema form, go to the **Webhooks** tab.
2. Add a webhook with a destination URL.
3. Select which events trigger the webhook (create, write, delete).
4. Optionally set a secret key for HMAC-SHA256 payload signing.
5. Add custom headers if the receiving system requires them.

**Scheduled Exports:**

1. In the schema form, go to the **Schedules** tab.
2. Add a schedule with the desired interval.
3. Choose the output format (JSON or JSON Lines) and destination
   (Odoo attachment or HTTP POST).
4. Enable **Incremental** to only export records changed since the last run.
