"""
Unit tests for E-Commerce Returns Automation Engine.
"""
import unittest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from returns_engine.policy_rules import ReturnPolicyRules
from returns_engine.rma_engine import RMAEngine
from returns_engine.integrations import HelpdeskDispatcher

class TestReturnsAutomation(unittest.TestCase):
    def setUp(self):
        self.engine = RMAEngine()

    def test_eligible_standard_return(self):
        recent_date = datetime.now() - timedelta(days=5)
        res = self.engine.create_return_request(
            order_number="SHP-9481",
            customer_email="sarah.j@example.com",
            item_id="item_01",
            item_name="Merino Wool Cyber Hoodie",
            item_price=128.00,
            purchase_date=recent_date,
            tags=["hoodies", "apparel"],
            return_type="REFUND"
        )
        self.assertEqual(res["status"], "APPROVED")
        self.assertIsNotNone(res["rma_number"])
        self.assertTrue(res["rma_number"].startswith("RMA-"))
        self.assertIn("https://shipping.symidic.xyz/labels/", res["prepaid_label_url"])
        self.assertEqual(res["estimated_refund"], 128.00)

    def test_size_exchange_authorization(self):
        recent_date = datetime.now() - timedelta(days=3)
        res = self.engine.create_return_request(
            order_number="SHP-1024",
            customer_email="marcus.v@example.com",
            item_id="item_02",
            item_name="Stealth Cargo Pants",
            item_price=95.00,
            purchase_date=recent_date,
            tags=["apparel", "pants"],
            return_type="EXCHANGE",
            desired_exchange_size="XL"
        )
        self.assertEqual(res["status"], "APPROVED")
        self.assertEqual(res["desired_exchange_size"], "XL")
        self.assertEqual(res["estimated_refund"], 0.0)

    def test_expired_return_window_rejected(self):
        old_date = datetime.now() - timedelta(days=45)
        res = self.engine.create_return_request(
            order_number="SHP-5012",
            customer_email="expired@example.com",
            item_id="item_03",
            item_name="Classic Beanie",
            item_price=35.00,
            purchase_date=old_date,
            tags=["accessories"]
        )
        self.assertEqual(res["status"], "REJECTED")
        self.assertIsNone(res["rma_number"])
        self.assertIn("expired", res["reason"].lower())

    def test_final_sale_clearance_rejected(self):
        recent_date = datetime.now() - timedelta(days=2)
        res = self.engine.create_return_request(
            order_number="SHP-9901",
            customer_email="clearance@example.com",
            item_id="item_04",
            item_name="Clearance Sunglasses",
            item_price=20.00,
            purchase_date=recent_date,
            tags=["accessories", "final_sale"]
        )
        self.assertEqual(res["status"], "REJECTED")
        self.assertIn("final_sale", res["reason"])

    def test_transit_damage_immediate_override(self):
        # Even past 30 days, damaged goods get replaced
        old_date = datetime.now() - timedelta(days=40)
        res = self.engine.create_return_request(
            order_number="SHP-3341",
            customer_email="damaged@example.com",
            item_id="item_05",
            item_name="Ceramic Cyber Mug",
            item_price=45.00,
            purchase_date=old_date,
            tags=["home", "final_sale"],
            is_damaged=True
        )
        self.assertEqual(res["status"], "APPROVED")
        self.assertIn("damage guarantee", res["reason"].lower())

    def test_helpdesk_ticket_dispatch(self):
        recent_date = datetime.now() - timedelta(days=1)
        rma = self.engine.create_return_request(
            order_number="SHP-9481",
            customer_email="sarah.j@example.com",
            item_id="item_01",
            item_name="Cyber Hoodie",
            item_price=128.00,
            purchase_date=recent_date,
            tags=["apparel"]
        )
        ticket = HelpdeskDispatcher.sync_to_helpdesk(rma)
        self.assertTrue(ticket["synced"])
        self.assertIn("TICK-RMA-", ticket["ticket_id"])

if __name__ == "__main__":
    unittest.main()
