# -*- coding: utf-8 -*-
{
    'name': 'Transaction Report',
    'version': '1.2',
    'category': 'Invoice',
    'sequence': 10,
    'summary': 'Transaction Report',
    'author': "OODU IMPLEMENTERS PRIVATE LIMITED",
    'website': "https://www.odooimplementers.com/",
    'depends': ['base', 'account', 'l10n_in_edi', 'payment'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/transaction.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3', 
}
