# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Quality Inspection Report',
    "version": "12.0.1.0.0",
    'summary': '',
    'author':"Oodu Implementers",
    'description': """This module fetches data from quality inspection in PDF format""",
    'category': 'Accounts',
    'depends': ['base', 'stock', 'oi_shs_quality_inspection'],
    'data': [
            'views/inspection_report_view.xml',
            'views/inspection_template_view.xml'
            ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
