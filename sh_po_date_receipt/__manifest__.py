# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Receipt By Scheduled Dates",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "version": "15.0.1",
    "category": "Purchases",
    "summary": """
Manage Receipts Module, Receipts By Date, Receipts By Time,
Merge Receipts, Receipts Based On Dates, Purchase Receipt Management,
Different Receipt For Different Date,Receipt By Dates Odoo
""",
    "description": """
This module group by receipts based on the scheduled date and time.
When you confirm the purchase order If two product scheduled date and
time is the same then it generates a single receipt for that But
it auto-generates different receipts if scheduled date and time are different.
You can easily manage the scheduled date of the product on the purchase order line.
""",
    "depends": ["purchase_stock"],
    "data": [
        "views/purchase_order_view.xml",
    ],
    "images": ["static/description/background.png", ],
    "auto_install": False,
    "installable": True,
    "application": True,
    "price": 20,
    "currency": "EUR"
}
