This module separates **AI chat and AI Agent authentication** from the credentials used by supporting OpenAI API services in Odoo Enterprise AI.

It allows organizations to route AI conversational queries, chat bots, and AI fields through an eligible **ChatGPT subscription** (Plus, Pro, Team, Enterprise) via an OAuth 2.0 Device Code grant flow, eliminating per-token generation costs for interactive chat while preserving the standard OpenAI developer API key for knowledge embeddings, Whisper voice transcription, and realtime sessions.

Supported configurations:

* **OpenAI API key only**: Standard Odoo setup (pay-per-token API for chat, embeddings, and voice).
* **ChatGPT subscription only**: ChatGPT subscription for chat and agents. Knowledge embeddings and voice remain unconfigured.
* **Mixed / Hybrid**: ChatGPT subscription for chat and agents; OpenAI developer API key for embeddings and voice.
