Once installed and configured, QWeb PDF reports use Paper Muncher automatically
when the binary is available and `report.pdf_engine` is set to `auto` or
`paper-muncher`.

Check the engine status:

```python
env["ir.actions.report"].get_wkhtmltopdf_state()
```

Returns `ok` when Paper Muncher is available with `auto` or `paper-muncher`.
Returns `install` when `paper-muncher` is forced but the binary is missing.

When generating PDFs, look for log lines prefixed with `PDF engine:`:

- `PDF engine: Paper-Muncher (...)`: rendering started with Paper Muncher
- `PDF engine: Paper-Muncher completed (...)`: PDF generated successfully
- `PDF engine: wkhtmltopdf (...)`: fallback to wkhtmltopdf

Low-level HTTP-over-pipe details are logged at `DEBUG` level only.
