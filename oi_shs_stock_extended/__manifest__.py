# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Fields',
    'version': '12.0.1.0',
    'author': 'Odou Implementers Private Limited',
    'website': 'https://www.odooimplementers.com',
    'category': 'Inventory',
    'summary': 'Inherit Fields in stock',
    'description': """Additional fields are added in Stock""",
    'depends': ['base', 'stock', 'stock_picking_batch','mrp','sale'],
    'data': ['views/stock_fields_views.xml'],
    'installable': True,
    'auto_install': False
}
