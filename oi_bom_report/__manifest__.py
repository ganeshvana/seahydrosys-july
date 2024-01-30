# -*- coding: utf-8 -*-
{
    'name': "BOM Report",

    'summary': """
        BOM""",

    'description': """
        BOM Report
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp',
                'mrp_plm',
                'mrp_mps',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/bom_structure_xl.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
