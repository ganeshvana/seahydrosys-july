# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Export Invoice FX Without-Consignee',
    "version": "15.0.1.0.0",
    'summary': 'Export Invoice FX Without Consignee',
    'author':"Oodu Implementers Pvt. Ltd.",
    'description': """Export Invoice FX Without Consignee Document""",
    'category': 'Accounts',
    'depends': ['web', 'account', 'oi_shs_move_extended'],
    'data': [
            'views/export_invoice_fx_without_consignee_report.xml',
            'views/export_invoice_fx_without_consignee_template_view.xml'
            ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
