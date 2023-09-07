{
    'name': "Sea Hydrosys",
    'summary': """ Add menu in configuration to list out the defective type """,
    'description':"",
    'author': "OODU IMPLEMENTERS PRIVATE LIMITED",
    'website': "https://www.odooimplementers.com/",
    'category': 'Purchase',
    'version': '1.0',
    'depends': ['base','mrp'],
    'data': [
    	'security/ir.model.access.csv',
        # 'views/mrp_inspection.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
