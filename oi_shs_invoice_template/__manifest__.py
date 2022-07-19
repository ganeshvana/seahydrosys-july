# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Invoice Template Extended',
    "version": "15.0.1.0.0",
    'summary': 'Invoice Template Extended',
    'author': 'Oodu Implementers Pvt. Ltd',
    'description': """This module modifies content of Invoice Email Template""",
    'category': 'Sales',
    'depends': ['base', 'account'],
    'data': [

    'data/template_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
