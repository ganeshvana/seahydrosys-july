# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Payslip',
    "version": "1.0",
    'summary': '',
    'author':"Oodu Implementers Private Limited",
    'description': """This module fetches data from Payslip in PDF format""",
    'category': 'HR Payslip',
    'depends': ['base','hr','hr_payroll','hr_contract'],
    'data': [
            'views/payslip_report_view.xml',
            'views/payslip_template_view.xml',
            # 'views/hr_employee_view.xml',
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    

}
