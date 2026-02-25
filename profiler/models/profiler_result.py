# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import api, fields, models


class ProfilerResult(models.Model):
    _name = "profiler.result"
    _description = "Profiler Result"
    _order = "create_date desc"

    name = fields.Char(string="Function Name", required=True, index=True)
    stats_text = fields.Text(string="Profile Statistics", required=True)
    stats_json = fields.Text(string="Profile Statistics JSON")
    stats_binary = fields.Binary(string="Profile Binary Data", attachment=True)
    stats_callgrind = fields.Binary(string="Profile Callgrind Data", attachment=True)
    duration = fields.Float(string="Duration (seconds)")
    create_date = fields.Datetime(string="Execution Date", readonly=True, index=True)
    user_id = fields.Many2one(
        "res.users", string="User", default=lambda self: self.env.user, readonly=True
    )
    flamegraph_html = fields.Html(
        string="Flamegraph", compute="_compute_flamegraph_html", store=True
    )

    @api.depends("stats_binary")
    def _compute_flamegraph_html(self):
        for record in self:
            record.flamegraph_html = record._generate_flamegraph_html()

    def _generate_flamegraph_html(self):
        """Generate flamegraph from binary pstats data."""
        if not self.stats_binary:
            return (
                "<p>No binary profiling data available. "
                "Flamegraph requires stats_binary.</p>"
            )

        try:
            import base64
            import logging
            import os
            import subprocess
            import tempfile

            _logger = logging.getLogger(__name__)

            # When attachment=True, data is stored in ir.attachment
            # We need to retrieve the attachment manually with bin_size=False
            attachment = (
                self.env["ir.attachment"]
                .sudo()
                .search(
                    [
                        ("res_model", "=", self._name),
                        ("res_id", "=", self.id),
                        ("res_field", "=", "stats_binary"),
                    ],
                    limit=1,
                )
            )

            if not attachment:
                return "<p>No attachment found for stats_binary</p>"

            # Use with_context to ensure we get the full data, not just the size
            attachment = attachment.with_context(bin_size=False)

            # Get raw data from attachment - datas field contains base64 encoded data
            if not attachment.datas:
                return "<p>No data in attachment</p>"

            try:
                # Decode base64 to get raw binary pstats data
                stats_data = base64.b64decode(attachment.datas)
                _logger.info(
                    f"Stats data decoded successfully, length: {len(stats_data)} bytes"
                )
            except Exception as e:
                _logger.error(
                    f"Failed to decode base64: {e}, datas:"
                    f"{attachment.datas[:100] if attachment.datas else 'None'}"
                )
                return f"<p>Cannot decode attachment data: {str(e)}</p>"

            # Create temp files
            fd, pstats_path = tempfile.mkstemp(suffix=".pstats")
            svg_fd, svg_path = tempfile.mkstemp(suffix=".svg")

            try:
                # Write pstats data to temp file
                with os.fdopen(fd, "wb") as f:
                    f.write(stats_data)
                os.close(svg_fd)

                # Generate SVG flamegraph using flameprof
                try:
                    result = subprocess.run(
                        ["flameprof", pstats_path],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else "Unknown error"
                        _logger.warning(f"flameprof failed: {error_msg}")
                        return f"""
                        <div style="padding: 20px; background-color: #fff3cd;
                            border: 1px solid #ffc107; border-radius: 4px;">
                            <h4>⚠️ Flamegraph Generation Failed</h4>
                            <p>Flameprof encountered an error processing this profile
                            data.
                            This is a known limitation with certain
                            profiling data structures.</p>
                            <details>
                                <summary>Error Details</summary>
                                <pre style="background: #f5f5f5; padding: 10px;
                                overflow-x: auto;">{error_msg}</pre>
                            </details>
                            <p><strong>Alternative:</strong>
                            Use the <em>Download .pstats</em>
                            button and visualize with external tools:</p>
                            <ul>
                                <li><code>gprof2dot -f pstats profile.pstats
                                | dot -Tpng -o output.png</code></li>
                                <li><code>snakeviz profile.pstats</code></li>
                            </ul>
                        </div>
                        """

                    with open(svg_path, "w") as svg_file:
                        svg_file.write(result.stdout)
                except FileNotFoundError:
                    return """
                    <div style="padding: 20px; background-color: #f8d7da;
                        border: 1px solid #f5c6cb; border-radius: 4px;">
                        <h4>❌ Flameprof Not Installed</h4>
                        <p>The <code>flameprof</code> package is not installed
                        in your environment.</p>
                        <p><strong>To enable flamegraphs, install it:</strong></p>
                        <pre style="background: #f5f5f5; padding: 10px;">
                            pip install flameprof
                        </pre>
                        <p>
                            <strong>Alternative:</strong>
                            Use the <em>Download .pstats</em> button and visualize with
                            other tools like gprof2dot or snakeviz.
                        </p>
                    </div>
                    """
                except subprocess.TimeoutExpired:
                    return "<p>Flamegraph generation timed out (>30s)</p>"
                except Exception as e:
                    _logger.error(f"Unexpected error in flameprof: {e}")
                    return f"<p>Unexpected error generating flamegraph: {str(e)}</p>"

                # Convert SVG to PNG using cairosvg to avoid SVG rendering issues
                try:
                    import cairosvg

                    png_fd, png_path = tempfile.mkstemp(suffix=".png")
                    os.close(png_fd)

                    with open(svg_path) as svg_file:
                        svg_content = svg_file.read()

                    # Convert SVG to PNG
                    cairosvg.svg2png(
                        bytestring=svg_content.encode("utf-8"),
                        write_to=png_path,
                        output_width=1600,
                    )  # Set a reasonable width

                    # Read PNG and encode as base64 for embedding
                    with open(png_path, "rb") as png_file:
                        png_data = base64.b64encode(png_file.read()).decode("utf-8")

                    # Clean up PNG temp file
                    os.unlink(png_path)

                    # Embed PNG as data URL
                    html = f"""
                    <style>
                        .flamegraph-wrapper {{
                            width: 100%;
                            overflow: auto;
                            background: #ffffff;
                            border: 1px solid #ddd;
                            padding: 20px;
                            box-sizing: border-box;
                        }}
                        .flamegraph-wrapper img {{
                            display: block;
                            max-width: 100%;
                            height: auto;
                        }}
                    </style>
                    <div class="flamegraph-wrapper">
                        <img src="data:image/png;base64,{png_data}" alt="Flamegraph" />
                    </div>
                    """
                    return html

                except ImportError:
                    _logger.warning("cairosvg not available, falling back to SVG")
                    # Fallback to SVG if cairosvg is not available
                    with open(svg_path) as svg_file:
                        svg_content = svg_file.read()

                    html = f"""
                    <style>
                        .flamegraph-wrapper {{
                            width: 100%;
                            min-height: 800px;
                            overflow: auto;
                            background: #ffffff;
                            border: 1px solid #ddd;
                            padding: 20px;
                            box-sizing: border-box;
                        }}
                        .flamegraph-wrapper svg {{
                            display: block;
                            max-width: 100%;
                            height: auto;
                        }}
                        .flamegraph-wrapper .func_g {{
                            cursor: pointer;
                        }}
                    </style>
                    <div class="flamegraph-wrapper">
                        {svg_content}
                    </div>
                    """
                    return html

            finally:
                # Cleanup temp files
                os.unlink(pstats_path)
                os.unlink(svg_path)

        except ImportError:
            return (
                "<p>flameprof is not installed. "
                "Please install it: pip install flameprof</p>"
            )
        except subprocess.TimeoutExpired:
            return "<p>Flamegraph generation timed out (>30s)</p>"
        except Exception as e:
            return f"<p>Error generating flamegraph: {str(e)}</p>"

    def action_download_pstats(self):
        """Download pstats file for external analysis with gprof2dot."""
        self.ensure_one()
        if not self.stats_binary:
            raise ValueError("No binary stats data available for this profile")

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/profiler.result/{self.id}/"
            f"stats_binary/{self.name}.pstats?download=true",
            "target": "new",
        }

    def action_download_callgrind(self):
        """Download callgrind file for external analysis with qcachegrind."""
        self.ensure_one()
        if not self.stats_callgrind:
            raise ValueError("No callgrind data available for this profile")

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/profiler.result/{self.id}/"
            f"stats_callgrind/{self.name}.callgrind?download=true",
            "target": "new",
        }
