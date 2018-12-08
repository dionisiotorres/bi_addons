# -*- coding: utf-8 -*-
{
    'name': "BI Employee Resignation",
    'summary': "BI Employee Resignation",
    'description': """ 
        This module add employee resignation.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['bi_hr_customizations', 'bi_employee_warehouse'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_resignation_view.xml',
        'views/menu_item_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
