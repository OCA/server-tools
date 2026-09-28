# Copyright - 2015-2026 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def get_message_body(email, subject):
    """Get Message Body, as returned by fetch() from connection.

    fetch returns a list of tuples with the message information.
    """
    return [
        (
            "1 (RFC822 {1149}",
            "Return-Path: <ronald@acme.com>\r\n"
            "Delivered-To: demo@yourcompany.example.com\r\n"
            "Received: from localhost (localhost [127.0.0.1])\r\n"
            "\tby vanaheim.acme.com (Postfix) with ESMTP id 14A3183163\r\n"
            "\tfor <demo@yourcompany.example.com>;"
            " Wed, 23 Jul 2025 16:03:52 +0200 (CEST)\r\n"
            "To: Test User <nonexistingemail@yourcompany.example.com>\r\n"
            f"From: Reynaert de Vos <{email}>\r\n"
            f"Subject: {subject}\r\n"
            "Message-ID: <485a8041-d560-a981-5afc-d31c1f136748@acme.com>\r\n"
            "Date: Mon, 26 Mar 2018 16:03:51 +0200\r\n"
            "User-Agent: Mock Test\r\n"
            "MIME-Version: 1.0\r\n"
            "Content-Type: text/plain; charset=utf-8\r\n"
            "Content-Language: en-US\r\n"
            "Content-Transfer-Encoding: 7bit\r\n\r\n"
            "Hallo Wereld!\r\n",
        )
    ]
