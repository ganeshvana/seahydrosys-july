# -*- coding: utf-8 -*-

{
'name' : 'Customer - Access ',
'version' : '12.0',
'author' : 'Oodu Implementers Private Limited',
'website' : 'http://www.odooimplementers.com',
'category' : 'Accounting',
'depends' : ['base', 'account','sale','purchase','stock','account_accountant','helpdesk',
             'l10n_in_sale','sale_mrp','sale_crm','sale_stock','sale_purchase','sale_management','sale_project',
             'purchase_requisition','mrp_subcontracting_purchase','l10n_in_purchase',
             'purchase_mrp','purchase_stock','portal','utm',
            ],
'description' : 'This module contains group for billing which restricts users from Invoice, Credit&Debit Note Validation and Journal Entry Posting',
'summary': 'Accounts Customer – User Permissions',
'data' : [
    'security/account_view.xml',
    'views/account_permissions.xml',

    ],
'installable': True,
'license': 'LGPL-3',
}