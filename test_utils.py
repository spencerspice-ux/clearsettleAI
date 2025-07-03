import unittest
from utils import validate_transaction, normalize_status, normalize_field, normalize_transaction

class TestUtils(unittest.TestCase):
    def test_validate_transaction(self):
        seen_ids = set()
        valid_txn = {"transaction_id": "123", "status": "completed", "ISIN": "US1234567890"}
        invalid_txn = {"transaction_id": "123", "status": "completed"}  # Missing ISIN

        self.assertTrue(validate_transaction(valid_txn, seen_ids))
        self.assertFalse(validate_transaction(invalid_txn, seen_ids))
        self.assertFalse(validate_transaction(valid_txn, seen_ids))  # Duplicate ID

    def test_validate_transaction_edge_cases(self):
        seen_ids = set()
        invalid_txn_type = {"transaction_id": 123, "status": "completed", "ISIN": "US1234567890"}  # ID as int
        extra_field_txn = {"transaction_id": "124", "status": "completed", "ISIN": "US1234567890", "extra": "field"}

        self.assertFalse(validate_transaction(invalid_txn_type, seen_ids))  # Invalid type
        self.assertTrue(validate_transaction(extra_field_txn, seen_ids))  # Extra fields are ignored

    def test_normalize_status(self):
        self.assertEqual(normalize_status(" Settled "), "settled")
        self.assertEqual(normalize_status("FAILED"), "failed")
        self.assertEqual(normalize_status("   "), "")  # Whitespace only
        self.assertEqual(normalize_status("Settled!"), "settled!")  # Special characters
        self.assertIsNone(normalize_status(None))

    def test_normalize_field(self):
        self.assertEqual(normalize_field(" Counterparty A "), "counterparty a")
        self.assertEqual(normalize_field("ASSET_TYPE"), "asset_type")
        self.assertEqual(normalize_field("   "), "")  # Whitespace only
        self.assertEqual(normalize_field("Field@123"), "field@123")  # Special characters
        self.assertIsNone(normalize_field(None))

    def test_normalize_transaction(self):
        txn = {
            "status": " Settled ",
            "asset_type": " Bond ",
            "counterparty": " Counterparty A ",
            "transaction_id": "123"
        }
        normalized_txn = normalize_transaction(txn)
        self.assertEqual(normalized_txn["status"], "settled")
        self.assertEqual(normalized_txn["asset_type"], "bond")
        self.assertEqual(normalized_txn["counterparty"], "counterparty a")
        self.assertEqual(normalized_txn["transaction_id"], "123")  # Unchanged field

        # Test with missing fields
        partial_txn = {"status": "FAILED"}
        normalized_partial_txn = normalize_transaction(partial_txn)
        self.assertEqual(normalized_partial_txn["status"], "failed")
        self.assertNotIn("asset_type", normalized_partial_txn)  # Field not present
        self.assertNotIn("counterparty", normalized_partial_txn)  # Field not present

if __name__ == "__main__":
    unittest.main()