# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 WebLine Apps 
##############################################################################

{
    'name': 'Product Advance Features',
    'version': '15.0.1.0',
    'category': 'product',
    'sequence': 0,
    'description': """
        Product Advance Features 
    """,
    'summary': """
        Product Advance Features used to Restrict for particular user, 
        this apps provide Hide Sale Price , Hide Cost Price , Read-only Sale Unit Price ,
        Read-only Purchase Unit Price , Read-only Invoice Unit Price , Read-only Sale order Taxes ,
        
        Read-only Purchase order Taxes , Read-only Invoice Taxes , Restrict To change unit price ,
        product Sale price hide , hide product cost price hide , restrict product cost price restrict ,
        restrict product sale price restrict , readonly Sale Unit Price readonly , readonly Sale order Unit Price readonly ,
        readonly Sales Unit Price readonly , readonly sales order Unit Price readonly , readonly sale price readonly ,
        
        
        readonly quotation Unit Price readonly , readonly quotation order Unit Price readonly ,
        readonly quotation price readonly , restrict sale unit price restrict , restrict sale order unit price restrict ,
        
        
        readonly purchase Unit Price readonly , readonly purchase order Unit Price readonly ,
        readonly purchase price readonly , restrict purchase unit price restrict ,
        
        readonly Invoice Unit Price readonly , readonly customer invoice price readonly , restrict invoice price restrict , 
        readonly Invoice Price readonly , 
        
        readonly bill Unit Price readonly , readonly vendor bill price readonly , restrict bill price restrict , 
        readonly bill Price readonly  ,
        
        readonly quotation Tax readonly , readonly sale order tax price readonly , restrict sale order tax restrict , restrict sale taxes ,
        
        
        readonly Purchase order tax readonly , readonly Purchase order Taxes readonly ,
        restrict Purchase order tax restrict , restrict Purchase taxes restrict , 
        
        readonly Invoice tax readonly , readonly customer invoice tax readonly , readonly customer invoice taxes readonly ,
        restrict customer invoice tax restrict , restrict customer invoice taxes restrict , 
        
        readonly bill tax readonly , readonly vendor bill tax readonly , readonly vendor bill taxes readonly ,
        restrict vendor bill tax restrict , restrict vendor bill taxes restrict ,
        
    """,
    'author': 'webline apps',
    'website': 'weblineapps@gmail.com ',
    'depends': ['sale','account','purchase'],
    'data': [
        'security/security.xml',
        'views/product_templet_view.xml',
        'views/sale_order_view.xml',
    ],
    'price': 6.00,
    'images' : ['static/description/baner.png'],
	'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
