# -*- coding: utf-8 -*-
{
    'name': "BI Employee Move Request",
    'summary': "BI Employee Move Request",
    'description': """ 
        This module add fields to employee contract effect in payslip.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['bi_employee_warehouse', 'hr_payroll_account', ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_move_request_view.xml',
        'views/menu_item_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
