# -*- coding: utf-8 -*-

{
    'name': 'Sea Hydosys Manufacturing Add fields',
    'category': 'Company',
    'summary': 'Manufacturing inherit function',
    'version': '15.0',
    'author': 'oodu implementers ',
    'description': """""",
    'depends': ['base','mrp','purchase','quality_mrp','stock',],
    'application': True,
    'data': [
        'security/account_view.xml',
        'views/inherit.xml',



    ],
}
