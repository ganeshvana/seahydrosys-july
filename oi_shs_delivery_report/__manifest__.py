# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Delivery Report',
    'author': 'Itara IT Solutions Private Limited',
    'website': 'https://www.itarait.com',
    'category': 'Report',
    'summary': 'GRN Report',
    'description': """GRN customized report.
    """,
    'depends': ['base', 'web', 'purchase', 'stock', 'oi_shs_stock_fields'],
    'data': ['report/menu.xml', 'report/grn_report_view.xml', 'report/sc_material_out_report.xml'],
    'installable': True,
    'auto_install': False
}
