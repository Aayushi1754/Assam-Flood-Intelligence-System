#completed
import unittest
from unittest.mock import MagicMock, patch

from db_operations import (
    get_all_requests,
    get_resource_inventory,
    get_pending_requests,
    get_allocation_history,
    update_request_status,
    allocate_resource,
    add_relief_request,
    get_resources_by_category,
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
            {
                "request_id": "REQ001",
                "resource_name": "water",
                "quantity": 10,
            }
        ]

        result = get_allocation_history()

        self.assertEqual(result[0]["quantity"], 10)

    @patch("db_operations.get_connection")
    def test_add_relief_request_with_nlp_fields(self, mock_connection):
        mock_conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
        mock_cursor.fetchone.return_value = ("REQ101",)

        result = add_relief_request(
            request_id="REQ101",
            location="Guwahati",
            need="Food",
            urgency_score=8.5,
            people_affected=20,
            arrival_time=30,
            source_text="Urgent food needed for 20 people",
            extracted_keywords=["food", "urgent"],
            urgency_level="high",
        )

        self.assertEqual(result, "REQ101")

        executed_query = mock_cursor.execute.call_args
        self.assertIn("extracted_keywords", executed_query.args[0])
        self.assertIn("urgency_level", executed_query.args[0])
        self.assertEqual(executed_query.args[1][-2], ["food", "urgent"])
        self.assertEqual(executed_query.args[1][-1], "high")

    def test_add_relief_request_rejects_invalid_keywords(self):
        with self.assertRaises(ValueError):
            add_relief_request(
                request_id="REQ102",
                location="Guwahati",
                need="Food",
                urgency_score=5.0,
                people_affected=10,
                arrival_time=20,
                extracted_keywords="food, urgent",
                urgency_level="medium",
            )

    def test_update_request_status_rejects_invalid_status(self):
        with self.assertRaises(ValueError):
            update_request_status("REQ001", "invalid_status")

    def test_allocate_resource_rejects_zero_quantity(self):
        with self.assertRaises(ValueError):
            allocate_resource("REQ001", "water", 0)

    def test_allocate_resource_rejects_negative_quantity(self):
        with self.assertRaises(ValueError):
            allocate_resource("REQ001", "water", -5)

    # Resource category tests

    def test_get_resources_by_category_rejects_invalid_category(self):
        with self.assertRaises(ValueError):
            get_resources_by_category("Electronics")

    def test_get_resources_by_category_rejects_empty_category(self):
        with self.assertRaises(ValueError):
            get_resources_by_category("")

    @patch("db_operations.get_connection")
    def test_get_resources_by_category_returns_available_resources(
        self, mock_connection
    ):
        mock_conn = MagicMock()
        mock_connection.return_value.__enter__.return_value = mock_conn

        mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
        mock_cursor.fetchall.return_value = [
            {
                "resource_id": 1,
                "resource_name": "water",
                "resource_category": "Water",
                "available_quantity": 100,
                "unit": "litres",
                "warehouse_location": "Guwahati",
            }
        ]

        result = get_resources_by_category("Water")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["resource_category"], "Water")
        self.assertEqual(result[0]["available_quantity"], 100)

        executed_query = mock_cursor.execute.call_args
        self.assertIn("resource_category = %s", executed_query.args[0])
        self.assertIn("available_quantity > 0", executed_query.args[0])
        self.assertEqual(executed_query.args[1], ("Water",))


if __name__ == "__main__":
    unittest.main(verbosity=2)