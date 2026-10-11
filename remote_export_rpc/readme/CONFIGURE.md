## 1. Create a Remote Odoo Instance

Go to **Remote Export > Remote Instances** and create a record with:

- **Name**: a label for the connection.
- **URL**: base URL of the remote Odoo (e.g. `https://example.odoo.com`).
- **Database**: remote database name.
- **Username / Password**: credentials of a user with sufficient rights on
  the remote instance.

Click **Test Connection** to verify the credentials before saving.

## 2. Configure a Match Config for each model

Go to **Remote Export > Match Configurations** and create a record for every
model you want to export. Fields to set:

| Field | Description |
|---|---|
| **Model** | Local Odoo model to expose (e.g. `product.template`). |
| **Use External ID** | Look up the remote record by xmlid first (recommended). |
| **Match fields** | Fields used as a fallback key when no xmlid is found. |
| **Match strategy** | *Each field (OR)*: try each field independently. *All fields (AND)*: require every field to match (compound key). |
| **Export fields** | Fields sent on record creation. Empty = all stored scalar/many2one fields. |
| **Update fields** | Fields sent on record update. Empty = same as export fields. |
| **Operation** | Default operation proposed in the wizard. |
| **Recursive match** | Resolve many2one relations without xmlid using the target model's match config. |

Saving the configuration automatically creates a server action that appears
in the **Action** menu of the model's list and form views.
