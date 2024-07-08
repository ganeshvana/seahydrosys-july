# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Qty Control based on MO',
    'version': '12.0.1.0',
    'author': 'Oodu Implementers Private Limited',
    'website': 'https://www.odooimplementers.com',
    'category': 'Inventory',
    'summary': '',
    'description': """Qty Control based on MO""",
    'depends': ['base', 'stock','mrp','purchase','delivery'],
    'data': [
        # 'security/stock_security.xml',
        'wizard/purchase_resupply_report.xml',
        'views/stock_fields_views.xml'],
    'installable': True,
    'auto_install': False
}
