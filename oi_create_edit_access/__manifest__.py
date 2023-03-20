# -*- coding: utf-8 -*-

{
'name' : 'Customer - Access ',
'version' : '12.0',
'author' : 'Oodu Implementers Private Limited',
'website' : 'http://www.odooimplementers.com',
'category' : 'Accounting',
'depends' : ['base', 'account','sale','purchase','stock','account_accountant'],
'description' : 'This module contains group for billing which restricts users from Invoice, Credit&Debit Note Validation and Journal Entry Posting',
'summary': 'Accounts Customer – User Permissions',
'data' : [
    'security/account_view.xml',
    'views/account_permissions.xml',

    ],
'installable': True,
'license': 'LGPL-3',
}