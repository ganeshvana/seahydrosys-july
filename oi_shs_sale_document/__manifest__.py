# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Order Report Extended',
    "version": "15.0.1.0.0",
    'summary': 'Sales Report',
    'author': 'Oodu Implementers Pvt. Ltd',
    'description': """This module contains extended view of sale document""",
    'category': 'Sales',
    'depends': ['base', 'sale'],
    'data': [
    # 'views/purchase_view.xml',
    'views/sale_report_view.xml',

    'views/sale_report_extend.xml',
    'views/sale_report_without_price.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
