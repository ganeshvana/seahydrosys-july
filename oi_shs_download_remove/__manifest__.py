# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Document Download Remove",
    'version': '2.0',
    'category': 'Document',
    'sequence': 6,
    'author': 'OODU IMPLEMENTERS PRIVATE LIMITED',
    'summary': 'Document Download Remove',
    'depends': ['documents'],
    'website': 'www.odooimplementers.com',
    'data': [
        
    ],
    
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_qweb': [


            'oi_shs_download_remove/static/src/xml/*.xml',
        ],
        'web.assets_tests': [
            
        ],
    },
    'license': 'LGPL-3',
}
