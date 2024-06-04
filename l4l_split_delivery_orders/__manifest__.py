# -*- coding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2023 Leap4Logic Solutions PVT LTD
#    Email : sales@leap4logic.com
#################################################

{
    'name': "Split Delivery Orders",
    'category': 'Inventory',
    'version': '15.0.1.0',
    'sequence': 5,
    'summary': """Split Delivery Order, Delivery Order Splitting, Delivery Order, Transfer Split, Split Transfer Order, Splitting Of Transfer, Split Delivery Orders into Multiple Orders, Improve Inventory Handling and Logistical Flexibility, Transfer, Delivery, Sale Order, Purchase, Invoice, Bills""",
    'description': """This Module Enables The Splitting of Delivery Orders With Identical Types and Partners, Allowing Users to Manage and Distribute Orders More Flexibly.""",

    'author': 'Leap4Logic Solutions Private Limited',
    'website': 'https://leap4logic.com/',
    'depends': ['stock'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_split_delivery_order_view.xml',
        'views/stock_picking_extend_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': ['static/description/banner.png'],
    'price': '7.99',
    'currency': 'USD',
    'live_test_url': 'https://youtu.be/HoPle9JHt3g',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
