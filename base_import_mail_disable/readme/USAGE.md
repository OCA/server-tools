To verify the functionality of the module:

1. Go to any list view in Odoo (e.g., *Contacts*, *Sales Orders*, *Users*).
2. Click **Favorites > Import records**.
3. Upload your CSV/Excel file normally.
4. The module operates entirely in the background. It will automatically intercept the `model.load()` operation globally. All explicitly triggered outbound emails will be routed to the outgoing queue gracefully as "Cancelled," meaning zero notifications will reach end-user inboxes.
