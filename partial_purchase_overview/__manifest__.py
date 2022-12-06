# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    #  Information
    'name': 'Partial Purchase Overview',
    'version': '15.0.1.0.0',
    'summary': 'Partial Purchase Overview',
    'description': 'Partial Purchase Overview',
    'category': 'Purchase',

    # Author
    'author': 'Odoo PS',
    'website': 'https://www.odoo.com/',
    'license': 'LGPL-3',

    # Dependency
    'depends': ['purchase_stock'],
    'data': [
        'views/purchase_views.xml',
    ],

    # Other
    'application': False,
    'installable': True,
    'auto_install': False,
}
