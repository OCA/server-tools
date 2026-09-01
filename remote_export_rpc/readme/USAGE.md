Once a match configuration exists for a model, an **Remote Export** action
appears in the **Action** menu of its list and form views.

**Steps:**

1. Select one or more records in the list view (or open a single record).
2. Open **Action > Remote Export**.
3. In the wizard:
   - **Instances**: choose one or more target remote Odoo instances.
   - **Operation**: override the default operation for this run if needed.
   - **Use External ID**: toggle xmlid-based lookup.
   - **Match strategy**: switch between compound key and alternative keys.
   - **Override match fields**: optionally replace the configured match fields
     for this run only.
4. Click **Export** to start the synchronisation.
5. The wizard stays open and shows a result summary per instance:

   ```
   [my-remote] created: 3, updated: 1, skipped (exists): 0,
               skipped (missing): 0, errors: 0
   ```

   Any per-record error is listed above the summary line.
