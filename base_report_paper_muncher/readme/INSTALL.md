Install the `paper-muncher` system binary before enabling this module. Example
for Ubuntu 22.04 (Jammy):

```bash
curl -fsSL -o paper-muncher.deb \
  "https://github.com/odoo/paper-muncher/releases/download/v0.3.1-1/paper-muncher_v0.3.1-1_jammy_amd64.deb"
sudo apt install ./paper-muncher.deb
paper-muncher --help
```

If the binary is not installed via the `.deb` package, add
`/opt/paper-muncher/bin` to the `PATH` of the Odoo process.

The Python dependency `h11` is declared in the module manifest and listed in
`requirements.txt`. Install it in the Odoo Python environment if needed:

```bash
pip install h11
```

Then install the module as any other Odoo addon:

```bash
odoo -d <database> -i base_report_paper_muncher --stop-after-init
```

Paper Muncher is only supported on Linux and macOS.
