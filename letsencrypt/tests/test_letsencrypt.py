# Copyright 2018-2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import os
import shutil
from datetime import datetime, timedelta
from os import path

import mock

from odoo.exceptions import UserError, ValidationError
from odoo.tests import SingleTransactionCase

from ..models.letsencrypt import _get_challenge_dir, _get_data_dir

try:
    import dns.resolver
except ImportError:
    pass


CERT_DIR = path.join(path.dirname(__file__), "certs")


def _poll(order, deadline):
    order_resource = mock.Mock(["fullchain_pem"])
    order_resource.fullchain_pem = "chain"
    return order_resource


class TestLetsencrypt(SingleTransactionCase):
    def setUp(self):
        super().setUp()
        self.env["ir.config_parameter"].set_param(
            "web.base.url", "http://www.example.com"
        )
        self.env["res.config.settings"].create(
            {
                "letsencrypt_dns_provider": "shell",
                "letsencrypt_dns_shell_script": "touch /tmp/.letsencrypt_test",
                "letsencrypt_altnames": "www.example.com,*.example.com",
                "letsencrypt_reload_command": "echo reloaded",
            }
        ).set_values()

    def test_config_settings(self):
        setting_vals = self.env["res.config.settings"].default_get([])
        self.assertEqual(setting_vals["letsencrypt_dns_provider"], "shell")
        self.assertEqual(
            setting_vals["letsencrypt_dns_shell_script"],
            "touch /tmp/.letsencrypt_test",
        )
        self.assertEqual(
            setting_vals["letsencrypt_altnames"], "www.example.com,*.example.com"
        )
        self.assertEqual(setting_vals["letsencrypt_reload_command"], "echo reloaded")
        self.assertTrue(setting_vals["letsencrypt_needs_dns_provider"])
        self.assertFalse(setting_vals["letsencrypt_prefer_dns"])

        with self.assertRaises(ValidationError):
            self.env["res.config.settings"].create(
                {"letsencrypt_dns_shell_script": "# Empty script"}
            ).set_values()

    @mock.patch("acme.client.ClientV2.answer_challenge")
    @mock.patch("acme.client.ClientV2.poll_and_finalize", side_effect=_poll)
    def test_http_challenge(self, poll, _answer_challenge):
        letsencrypt = self.env["letsencrypt"]
        self.env["res.config.settings"].create(
            {"letsencrypt_altnames": ""}
        ).set_values()
        letsencrypt._cron()
        poll.assert_called()
        self.assertTrue(os.listdir(_get_challenge_dir()))
        self.assertFalse(path.isfile("/tmp/.letsencrypt_test"))
        self.assertTrue(path.isfile(path.join(_get_data_dir(), "www.example.com.crt")))

    # pylint: disable=unused-argument
    @mock.patch("odoo.addons.letsencrypt.models.letsencrypt.DNSUpdate")
    @mock.patch("dns.resolver.query")
    @mock.patch("time.sleep")
    @mock.patch("acme.client.ClientV2.answer_challenge")
    @mock.patch("acme.client.ClientV2.poll_and_finalize", side_effect=_poll)
    def test_dns_challenge(self, poll, answer_challenge, sleep, query, dnsupd):

        record = None

        def register_update(challenge, domain, token):
            nonlocal record
            record = mock.Mock()
            record.to_text.return_value = '"%s"' % token
            ret = mock.Mock()
            ret.challenge = challenge
            ret.domain = domain
            ret.token = token
            return ret

        dnsupd.side_effect = register_update

        ncalls = 0

        def query_effect(domain, rectype):
            nonlocal ncalls
            self.assertEqual(domain, "_acme-challenge.example.com.")
            self.assertEqual(rectype, "TXT")
            ncalls += 1
            if ncalls == 1:
                raise dns.resolver.NXDOMAIN
            elif ncalls == 2:
                wrong_record = mock.Mock()
                wrong_record.to_text.return_value = '"not right"'
                return [wrong_record]
            else:
                return [record]

        query.side_effect = query_effect

        self.install_certificate(days_left=10)
        self.env["letsencrypt"]._cron()
        poll.assert_called()
        self.assertEqual(ncalls, 3)
        self.assertTrue(path.isfile("/tmp/.letsencrypt_test"))
        self.assertTrue(path.isfile(path.join(_get_data_dir(), "www.example.com.crt")))

    def test_dns_challenge_error_on_missing_provider(self):
        self.env["res.config.settings"].create(
            {
                "letsencrypt_altnames": "*.example.com",
                "letsencrypt_dns_provider": False,
            }
        ).set_values()
        with self.assertRaises(UserError):
            self.env["letsencrypt"]._cron()

    def test_prefer_dns_setting(self):
        self.env["res.config.settings"].create(
            {"letsencrypt_altnames": "example.com", "letsencrypt_prefer_dns": True}
        ).set_values()
        # pylint: disable=no-value-for-parameter
        self.test_dns_challenge()

    def test_cascading(self):
        cascade = self.env["letsencrypt"]._cascade_domains
        self.assertEqual(
            cascade(
                [
                    "www.example.com",
                    "*.example.com",
                    "example.com",
                    "example.com",
                    "notexample.com",
                    "multi.sub.example.com",
                    "www2.example.com",
                    "unrelated.com",
                ]
            ),
            [
                "*.example.com",
                "example.com",
                "multi.sub.example.com",
                "notexample.com",
                "unrelated.com",
            ],
        )
        self.assertEqual(cascade([]), [])
        self.assertEqual(cascade(["*.example.com"]), ["*.example.com"])
        self.assertEqual(cascade(["www.example.com"]), ["www.example.com"])
        self.assertEqual(
            cascade(["www.example.com", "example.com"]),
            ["example.com", "www.example.com"],
        )

        with self.assertRaises(UserError):
            cascade(["www.*.example.com"])

        with self.assertRaises(UserError):
            cascade(["*.*.example.com"])

    def test_altnames_parsing(self):
        config = self.env["ir.config_parameter"]
        letsencrypt = self.env["letsencrypt"]

        self.assertEqual(
            letsencrypt._get_altnames(), ["www.example.com", "*.example.com"]
        )

        config.set_param("letsencrypt.altnames", "")
        self.assertEqual(letsencrypt._get_altnames(), ["www.example.com"])

        config.set_param("letsencrypt.altnames", "foobar.example.com")
        self.assertEqual(letsencrypt._get_altnames(), ["foobar.example.com"])

        config.set_param("letsencrypt.altnames", "example.com,example.org,example.net")
        self.assertEqual(
            letsencrypt._get_altnames(),
            ["example.com", "example.org", "example.net"],
        )

        config.set_param(
            "letsencrypt.altnames", "example.com, example.org\nexample.net"
        )
        self.assertEqual(
            letsencrypt._get_altnames(),
            ["example.com", "example.org", "example.net"],
        )

    def test_key_generation_and_retrieval(self):
        key_a1 = self.env["letsencrypt"]._get_key("a.key")
        key_a2 = self.env["letsencrypt"]._get_key("a.key")
        key_b = self.env["letsencrypt"]._get_key("b.key")
        self.assertIsInstance(key_a1, bytes)
        self.assertIsInstance(key_a2, bytes)
        self.assertIsInstance(key_b, bytes)
        self.assertTrue(path.isfile(path.join(_get_data_dir(), "a.key")))
        self.assertEqual(key_a1, key_a2)
        self.assertNotEqual(key_a1, key_b)

    @mock.patch("os.remove", side_effect=os.remove)
    @mock.patch(
        "odoo.addons.letsencrypt.models.letsencrypt.Letsencrypt._generate_key",
        side_effect=lambda: None,
    )
    def test_interrupted_key_writing(self, generate_key, remove):
        with self.assertRaises(TypeError):
            self.env["letsencrypt"]._get_key("a.key")
        self.assertFalse(path.isfile(path.join(_get_data_dir(), "a.key")))
        remove.assert_called()
        generate_key.assert_called()

    def test_domain_validation(self):
        self.env["letsencrypt"]._validate_domain("example.com")
        self.env["letsencrypt"]._validate_domain("www.example.com")

        with self.assertRaises(UserError):
            self.env["letsencrypt"]._validate_domain("1.1.1.1")
        with self.assertRaises(UserError):
            self.env["letsencrypt"]._validate_domain("192.168.1.1")
        with self.assertRaises(UserError):
            self.env["letsencrypt"]._validate_domain("localhost.localdomain")
        with self.assertRaises(UserError):
            self.env["letsencrypt"]._validate_domain("testdomain")
        with self.assertRaises(UserError):
            self.env["letsencrypt"]._validate_domain("::1")

    def test_young_certificate(self):
        self.install_certificate(60)
        self.assertFalse(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com", "*.example.com"],
            )
        )

    def test_old_certificate(self):
        self.install_certificate(20)
        self.assertTrue(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com", "*.example.com"],
            )
        )

    def test_expired_certificate(self):
        self.install_certificate(-10)
        self.assertTrue(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com", "*.example.com"],
            )
        )

    def test_missing_certificate(self):
        self.assertTrue(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com", "*.example.com"],
            )
        )

    def test_new_altnames(self):
        self.install_certificate(60, "www.example.com", ())
        self.assertTrue(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com", "*.example.com"],
            )
        )
        self.assertFalse(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com"],
            )
        )

    def test_legacy_certificate_without_altnames(self):
        self.install_certificate(60, use_altnames=False)
        self.assertFalse(
            self.env["letsencrypt"]._should_run(
                path.join(_get_data_dir(), "www.example.com.crt"),
                ["www.example.com"],
            )
        )

    def install_certificate(
        self,
        days_left,
        common_name="www.example.com",
        altnames=("*.example.com",),
        use_altnames=True,
    ):
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        not_after = datetime.now() + timedelta(days=days_left)
        not_before = not_after - timedelta(days=90)

        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        cert_builder = (
            x509.CertificateBuilder()
            .subject_name(
                x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, common_name)])
            )
            .issuer_name(
                x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "myca.biz")])
            )
            .not_valid_before(not_before)
            .not_valid_after(not_after)
            .serial_number(x509.random_serial_number())
            .public_key(key.public_key())
        )

        if use_altnames:
            cert_builder = cert_builder.add_extension(
                x509.SubjectAlternativeName(
                    [x509.DNSName(common_name)]
                    + [x509.DNSName(name) for name in altnames]
                ),
                critical=False,
            )

        cert = cert_builder.sign(key, hashes.SHA256(), default_backend())
        cert_file = path.join(_get_data_dir(), "%s.crt" % common_name)
        with open(cert_file, "wb") as file_:
            file_.write(cert.public_bytes(serialization.Encoding.PEM))

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(_get_data_dir(), ignore_errors=True)
        if path.isfile("/tmp/.letsencrypt_test"):
            os.remove("/tmp/.letsencrypt_test")
