Once configured:

1. Open any **AI Agent** record under **AI > Agents**.
2. Select any active ChatGPT model directly from the **LLM Model** dropdown (e.g. `GPT-5.6 Luna`, `GPT-5.6 Terra`, `GPT-5.5`, `GPT-5.4`, etc.).
3. Conversations initiated with the AI agent or chat bots will automatically stream responses through the authorized ChatGPT subscription without per-token charges.
4. Tokens are automatically refreshed every 2 hours via a background cron job (`ir.cron`), with concurrency protection across multi-worker environments.

Managing & Adding New Models
----------------------------

When OpenAI releases new models or deprecates older versions:

1. Navigate to **AI > Configuration > Settings**.
2. Under the connected ChatGPT section, click **Manage Models**.
3. To add a newly released OpenAI model (e.g., `GPT-5.7 Pro` with technical code `gpt-5.7-pro`), click **New** and enter the display name and technical model ID.
4. To deactivate an old or deprecated model, simply toggle its **Active** switch off.
5. The model selection on all AI Agents will update immediately across Odoo.
