# 2026  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64

from odoo.tests import TransactionCase


class TestAttachmentUnindexContent(TransactionCase):
    """Test cases for attachment_unindex_content module.

    This module disables the indexation of attachment content to:
    - Avoid duplicating data (file in filestore + content in database)
    - Improve performance (no text extraction from files)
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Attachment = cls.env["ir.attachment"]

        # Sample content for testing
        cls.test_text_content = b"This is a test file content for indexing verification"
        cls.test_text_b64 = base64.b64encode(cls.test_text_content)

    def test_attachment_index_content_disabled(self):
        """Test that index_content is not populated when creating attachment.

        The module should prevent content indexation by overriding the _index method
        to return False, which prevents the index_content field from being populated.
        """
        attachment = self.Attachment.create(
            {
                "name": "test_file.txt",
                "datas": self.test_text_b64,
                "mimetype": "text/plain",
            }
        )

        self.assertFalse(
            attachment.index_content,
            "index_content should be False (empty) when creating attachment "
            "because the module disables content indexation",
        )

    def test_attachment_index_method_returns_false(self):
        """Test that _index method always returns False.

        The core functionality of this module is to override the _index method
        to always return False, preventing any content from being indexed.
        """
        attachment = self.Attachment.create(
            {
                "name": "test_doc.txt",
                "datas": self.test_text_b64,
                "mimetype": "text/plain",
            }
        )

        # Call _index method directly to verify it returns False
        result = attachment._index(
            bin_data=self.test_text_content,
            mimetype="text/plain",
        )

        self.assertFalse(
            result,
            "_index method should always return False to disable indexation",
        )

    def test_attachment_with_checksum_parameter(self):
        """Test that _index method handles checksum parameter correctly."""
        attachment = self.Attachment.create(
            {
                "name": "test_with_checksum.pdf",
                "datas": b"UERGIGNvbnRlbnQ=",  # base64 of "PDF content"
                "mimetype": "application/pdf",
            }
        )

        # Call _index method with checksum parameter (introduced in later Odoo versions)
        result = attachment._index(
            bin_data=b"PDF test content",
            mimetype="application/pdf",
            checksum="dummy_checksum",
        )

        # Verify that _index returns False even with checksum
        self.assertFalse(
            result, "_index method should return False even with checksum parameter"
        )

    def test_existing_attachment_index_cleared(self):
        """Test that existing attachments with index_content get it cleared."""
        there_are_attachments = self.Attachment.search([], limit=2, order="id")
        self.assertTrue(there_are_attachments, "Should exists attachments")
        there_are_index = self.Attachment.search(
            [("index_content", "!=", False)], limit=1, order="id"
        )
        self.assertFalse(
            there_are_index, "Should not exists attachments with index_content"
        )

    def test_multiple_attachments_no_indexing(self):
        """Test that multiple attachments are created without indexing."""
        attachments = self.Attachment.create(
            [
                {
                    "name": f"test_file_{i}.txt",
                    "datas": b"VGVzdCBjb250ZW50IHtpfQ==",  # base64 encoded
                    "mimetype": "text/plain",
                }
                for i in range(5)
            ]
        )

        # Verify that none of the attachments have index_content populated
        for attachment in attachments:
            self.assertFalse(
                attachment.index_content,
                f"Attachment {attachment.name} should not have indexed content",
            )

    def test_different_file_types_no_indexing(self):
        """Test that different file types are not indexed."""
        file_types = [
            ("document.txt", "text/plain", b"VGV4dCBmaWxl"),
            ("document.pdf", "application/pdf", b"UERGIGZpbGU="),
            (
                "document.docx",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                b"RE9DWCBmaWxl",
            ),
            ("image.png", "image/png", b"UE5HIGltYWdl"),
            (
                "spreadsheet.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                b"WExTWCBmaWxl",
            ),
        ]

        for name, mimetype, datas in file_types:
            with self.subTest(name=name, mimetype=mimetype):
                attachment = self.Attachment.create(
                    {
                        "name": name,
                        "datas": datas,
                        "mimetype": mimetype,
                    }
                )

                self.assertFalse(
                    attachment.index_content,
                    f"Attachment {name} with mimetype {mimetype} should not be indexed",
                )

    def test_attachment_search_without_index(self):
        """Test that attachments can still be searched by name without indexing."""
        attachment = self.Attachment.create(
            {
                "name": "searchable_document.txt",
                "datas": b"U2VhcmNoYWJsZSBjb250ZW50",  # base64 of "Searchable content"
                "mimetype": "text/plain",
            }
        )

        # Search by name should still work
        found = self.Attachment.search([("name", "=", "searchable_document.txt")])

        self.assertEqual(
            len(found),
            1,
            "Should find attachment by name even without content indexing",
        )
        self.assertEqual(found.id, attachment.id)
        self.assertFalse(found.index_content, "Found attachment should not be indexed")
