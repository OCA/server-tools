The system parameter `report.pdf_engine` controls which PDF engine is used:

| Value | Behavior |
| ----- | -------- |
| `auto` (default) | Use Paper Muncher when the binary is available, otherwise wkhtmltopdf |
| `paper-muncher` | Force Paper Muncher; raise an error if the binary is missing |
| `wkhtmltopdf` | Always use wkhtmltopdf |

Change it from code:

```python
env["ir.config_parameter"].sudo().set_param("report.pdf_engine", "auto")
```

Or from **Settings > Technical > Parameters > System Parameters**, key
`report.pdf_engine`.

Optional environment variables for the Odoo process:

- `ODOO_PAPER_MUNCHER_FEATURE=1`: pass `--feature *=on` to the binary
- `ODOO_PAPER_MUNCHER_DEBUG=1`: pass `--debug http-client` to the binary. This
  flag is not sent by default in production. It is also enabled automatically
  when the module logger is set to `DEBUG`.
