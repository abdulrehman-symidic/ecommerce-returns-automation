# 🛡️ Autonomous E-Commerce Returns & Exchanges Engine

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Shopify Plus Compatible](https://img.shields.io/badge/Shopify-Plus_RMA-96BF48?style=for-the-badge&logo=shopify&logoColor=white)](https://shopify.dev)
[![Gorgias & Zendesk Sync](https://img.shields.io/badge/Helpdesk-Gorgias_%7C_Zendesk-1F8EFA?style=for-the-badge)](https://gorgias.com)
[![Tests: Passing](https://img.shields.io/badge/Tests-100%25_Passing-brightgreen?style=for-the-badge)](tests/test_returns.py)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> **Zero-touch Return Merchandise Authorization (RMA), instant prepaid label generation, and automated inventory exchange engine for Shopify brands.** Engineered by **[SYMIDIC](https://www.symidic.xyz)**.

---

## ⚡ Overview

Handling returns and size exchanges manually drains 15-25 hours per week for e-commerce brands. This engine provides an **autonomous RMA pipeline** that:
1. **Validates Eligibility Instantly:** Evaluates 30-day windows, non-refundable tags (`final_sale`, `clearance`), and condition criteria.
2. **Instant Prepaid Labels:** Auto-generates trackable return labels with unique RMA IDs.
3. **Automated Exchanges:** Reserves alternative sizes/colors in inventory to preserve the sale instead of defaulting to a cash refund.
4. **Bi-Directional Helpdesk Sync:** Automatically logs tickets and status updates into Gorgias, Zendesk, or Shopify Plus.

---

## 🏗️ RMA Workflow Flowchart

```mermaid
flowchart LR
    Customer([Customer Return Request]) --> PolicyEngine{Policy Eligibility Engine}
    PolicyEngine -- Window Expired (>30 Days) --> Reject([Reject with Clear Policy Explanation])
    PolicyEngine -- Final Sale / Restricted --> Reject
    PolicyEngine -- Eligible / Damaged Guarantee --> RMAGenerator[Generate RMA-2026-XXXX]
    
    RMAGenerator --> TypeCheck{Return Type?}
    TypeCheck -- EXCHANGE --> Reserve[Reserve Replacement Size in Inventory]
    TypeCheck -- REFUND --> Calc[Calculate Refund Total]
    
    Reserve --> Label[Issue Prepaid USPS/FedEx Label]
    Calc --> Label
    Label --> Dispatch[Dispatch Ticket to Gorgias / Zendesk]
```

---

## 🚀 Quickstart & Tests

### 1. Clone the Repository
```bash
git clone https://github.com/abdulrehman-symidic/ecommerce-returns-automation.git
cd ecommerce-returns-automation
```

### 2. Run Automated Unit Tests (100% Pass)
```bash
python -m unittest tests/test_returns.py
```

---

## 🧪 Python Usage Example

```python
from datetime import datetime, timedelta
from returns_engine.rma_engine import RMAEngine

engine = RMAEngine()

# Initiate an automated size exchange
result = engine.create_return_request(
    order_number="SHP-9481",
    customer_email="customer@example.com",
    item_id="item_01",
    item_name="Merino Wool Cyber Hoodie",
    item_price=128.00,
    purchase_date=datetime.now() - timedelta(days=4),
    tags=["apparel", "hoodies"],
    return_type="EXCHANGE",
    desired_exchange_size="L"
)

print(result)
```

**Output:**
```json
{
  "rma_number": "RMA-2026-F981AC",
  "status": "APPROVED",
  "order_number": "SHP-9481",
  "return_type": "EXCHANGE",
  "desired_exchange_size": "L",
  "prepaid_label_url": "https://shipping.symidic.xyz/labels/RMA-2026-F981AC.pdf",
  "carrier": "USPS Priority Return",
  "estimated_refund": 0.0,
  "reason": "Item is fully eligible for return or size exchange."
}
```

---

## 👨‍💻 Author & License
Architected by **Abdul Rehman** — Founder & Lead AI Systems Architect at **[SYMIDIC](https://www.symidic.xyz)**.  
Licensed under the [MIT License](LICENSE).
