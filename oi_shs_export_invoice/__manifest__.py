# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Export Invoice',
    "version": "15.0.1.0.0",
    'summary': 'Export Invoice',
    'author':"Oodu Implementers Pvt. Ltd.",
    'description': """Export Invoice Document""",
    'category': 'Accounts',
    'depends': ['web', 'account', 'oi_shs_move_extended'],
    'data': [
            'views/export_invoice_report_view.xml',
            'views/export_invoice_template_view.xml'
            ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
