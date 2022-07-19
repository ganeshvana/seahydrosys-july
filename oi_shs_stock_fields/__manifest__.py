# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Fields',
    'version': '12.0.1.0',
    'author': 'Itara IT Solutions Private Limited',
    'website': 'https://www.itarait.com',
    'category': 'Fields',
    'summary': 'Inherit Fields in stock',
    'description': """Additional fields are added in Stock""",
    'depends': ['base', 'stock','mrp', 'purchase_stock'],
    'data': ['views/stock_fields_views.xml'],
    'installable': True,
    'auto_install': False
}
