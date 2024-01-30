# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Additional fields in purchase & Report',
    "version": "15.0.1.0.0",
    'summary': 'Additional fields in purchase & Report',
    'author': 'Oodu Implementers Pvt. Ltd.',
    'description': """This module contains fields additionally added to purchase form & Report""",
    'category': 'purchase',
    'depends': ['base', 'purchase'],
    'data': ['views/purchase_view.xml','views/purchase_report_extend.xml','views/purchase_order_view.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,

}
