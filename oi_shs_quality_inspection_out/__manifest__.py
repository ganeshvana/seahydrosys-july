# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inspection - OUT',
    'version': '15.0.1.0',
    'author': 'Oodu Implementers Private Limited',
    'website': 'https://www.odooimplementers.com',
    'category': 'Inventory',
    'summary': '',
    'description': """""",
    'depends': ['base','stock','quality_control'],
    'data': [
    'security/ir.model.access.csv',
    'views/inspection_out_view.xml',
    'views/inspection_template_out_view.xml'],
    'installable': True,
    'auto_install': False
}
