# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Export Invoice - FX',
    "version": "16.0.1.0.0",
    'summary': 'Export Invoice',
    'author':"Oodu Implementers Pvt. Ltd.",
    'description': """Export Invoice Document""",
    'category': 'Accounts',
    'depends': ['base', 'account', 'oi_shs_exchange_rate','stock_account'],
    'data': [
            'views/export_invoice_report_view.xml',
            'views/export_invoice_template_view.xml',
            'views/invoice_report.xml'
            ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
