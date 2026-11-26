To configure this module:

1. Navigate to **AI > Configuration > Settings** (or **General Settings > AI Providers**) as a Settings Administrator (`base.group_system`).
2. Under **Use your own ChatGPT / OpenAI account**, choose **ChatGPT Subscription (OAuth)** under Connection Type.
3. Click **Connect ChatGPT Subscription** to launch the device authentication wizard.
4. Follow the prompt to visit `https://auth.openai.com/codex/device` and input the provided one-time code to authorize the Odoo instance.
5. Return to Odoo and click **Verify & Connect**.
6. (Optional) In the same section, expand the optional API key section to provide a developer API key if knowledge base embeddings (RAG) or voice transcription are also needed.
7. Use the **Sync Models** and **Test Connection** buttons to verify credentials and synchronize available models.
