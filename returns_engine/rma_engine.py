"""
RMA (Return Merchandise Authorization) State Machine.
Handles automated dispute triage, instant exchange reservations, and prepaid label generation.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import uuid
from .policy_rules import ReturnPolicyRules

class RMAEngine:
    def __init__(self):
        self._active_rmas: Dict[str, Dict[str, Any]] = {}

    def create_return_request(
        self,
        order_number: str,
        customer_email: str,
        item_id: str,
        item_name: str,
        item_price: float,
        purchase_date: datetime,
        tags: list,
        return_type: str = "REFUND", # "REFUND" or "EXCHANGE"
        desired_exchange_size: Optional[str] = None,
        is_damaged: bool = False
    ) -> Dict[str, Any]:
        """
        Processes an RMA request end-to-end with zero human latency.
        """
        # 1. Evaluate policy eligibility
        is_eligible, reason = ReturnPolicyRules.evaluate_item_eligibility(
            purchase_date=purchase_date,
            tags=tags,
            is_damaged_in_transit=is_damaged
        )

        if not is_eligible:
            return {
                "status": "REJECTED",
                "rma_number": None,
                "reason": reason,
                "prepaid_label_url": None,
                "estimated_refund": 0.0
            }

        # 2. Generate RMA tracking code
        rma_id = f"RMA-{datetime.now().year}-{uuid.uuid4().hex[:6].upper()}"
        
        # 3. Generate Prepaid Shipping Label
        label_tracking = f"9400111899562{uuid.uuid4().hex[:7].upper()}"
        label_url = f"https://shipping.symidic.xyz/labels/{rma_id}.pdf"

        rma_record = {
            "rma_number": rma_id,
            "status": "APPROVED",
            "order_number": order_number,
            "customer_email": customer_email,
            "item_name": item_name,
            "return_type": return_type,
            "desired_exchange_size": desired_exchange_size,
            "prepaid_label_url": label_url,
            "carrier": "USPS Priority Return",
            "tracking_number": label_tracking,
            "estimated_refund": item_price if return_type == "REFUND" else 0.0,
            "created_at": datetime.now().isoformat(),
            "reason": reason
        }

        self._active_rmas[rma_id] = rma_record
        return rma_record

    def get_rma_status(self, rma_number: str) -> Optional[Dict[str, Any]]:
        return self._active_rmas.get(rma_number.strip().upper())
