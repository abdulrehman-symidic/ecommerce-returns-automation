"""
Return Policy Evaluation Rules & Constraints.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

class ReturnPolicyRules:
    DEFAULT_RETURN_WINDOW_DAYS = 30
    RESTRICTED_TAGS = {"final_sale", "clearance", "gift_card", "hygiene_sealed"}

    @classmethod
    def evaluate_item_eligibility(
        cls,
        purchase_date: datetime,
        tags: list,
        is_opened: bool = False,
        is_damaged_in_transit: bool = False,
        current_date: datetime = None
    ) -> Tuple[bool, str]:
        """
        Evaluates whether an item qualifies for a return or exchange.
        Returns: (is_eligible, reason)
        """
        now = current_date or datetime.now()
        
        # 1. Damaged in transit exception
        if is_damaged_in_transit:
            return True, "Instant replacement authorized under transit damage guarantee."

        # 2. Check restricted categories / tags
        for t in tags:
            clean_tag = t.strip().lower().replace(" ", "_")
            if clean_tag in cls.RESTRICTED_TAGS:
                return False, f"Item tagged as '{clean_tag}' is non-refundable."

        # 3. Check return window
        days_elapsed = (now - purchase_date).days
        if days_elapsed > cls.DEFAULT_RETURN_WINDOW_DAYS:
            return False, f"Return window expired ({days_elapsed} days elapsed, maximum allowed: {cls.DEFAULT_RETURN_WINDOW_DAYS} days)."

        # 4. Check opened hygiene items
        if is_opened and "personal_care" in tags:
            return False, "Opened personal care or hygiene items cannot be returned."

        return True, "Item is fully eligible for return or size exchange."
