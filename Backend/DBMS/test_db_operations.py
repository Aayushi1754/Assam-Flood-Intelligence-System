
import unittest
from unittest.mock import MagicMock, patch

from db_operations import (
    get_all_requests,
    get_resource_inventory,
    get_pending_requests,
    get_allocation_history,
    update_request_status,
    allocate_resource,
)


class TestDBOperations(unittest.TestCase):

    @patch("db_operations.get_connection")
    def test_get_all_requests(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = [
            {"request_id": "REQ001", "location": "Dibrugarh"}
        ]

        result = get_all_requests()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["request_id"], "REQ001")

    @patch("db_operations.get_connection")
    def test_get_resource_inventory(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = [
            {"resource_name": "water", "available_quantity": 100}
        ]

        result = get_resource_inventory()

        self.assertEqual(result[0]["resource_name"], "water")

    @patch("db_operations.get_connection")
    def test_get_pending_requests(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = [
            {"request_id": "REQ003", "status": "pending"}
        ]

        result = get_pending_requests()

        self.assertEqual(result[0]["status"], "pending")

    @patch("db_operations.get_connection")
    def test_get_allocation_history(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value.fetchall.return_value = [
            {"request_id": "REQ001", "resource_name": "water", "quantity": 10}
        ]

        result = get_allocation_history()

        self.assertEqual(result[0]["quantity"], 10)

    def test_update_request_status_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            update_request_status("REQ001", "invalid_status")

    def test_allocate_resource_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            allocate_resource("REQ001", "water", 0)

    def test_allocate_resource_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            allocate_resource("REQ001", "water", -5)


if __name__ == "__main__":
    unittest.main(verbosity=2)