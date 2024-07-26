{
    'name': 'Add Vendor Type in Contacts',
    'version': '15.0',
    'category': 'Contacts',
    'depends': ['product'],
    'author': 'INKERP',
    'website': "https://www.INKERP.com",
    
    'data': [
        'security/security.xml',
        'views/vendor_type_view.xml',
        'views/res_partner_view.xml',
        'views/product_supplierinfo_view.xml',
        'security/ir.model.access.csv',
    ],
    
    'images': ['static/description/banner.png'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,
}
