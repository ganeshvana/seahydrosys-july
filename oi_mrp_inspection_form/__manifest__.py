# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Manufacturing Fields',
    'version': '12.0.1.0',
    'author': 'Odou Implementers Private Limited',
    'website': 'https://www.odooimplementers.com',
    'category': 'Manufacturing',
    'summary': 'Inherit Fields in stock',
    'description': """Additional fields are added in Manufacturing > Inspcetion""",
    'depends': ['base', 'stock', 'stock_picking_batch','mrp','sale','quality_control','oi_shs_quality_inspection','contacts'],
    'data': ['views/stock_fields_views.xml',
    'security/ir.model.access.csv',
    'views/inspection_report_view.xml',
    'views/inspection_template_view.xml',
    ],

    'installable': True,
    'auto_install': False
}
