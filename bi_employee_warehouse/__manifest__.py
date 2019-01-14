# -*- coding: utf-8 -*-
{
    'name': "BI Employee Warehouse",
    'summary': "BI Employee Warehouse",
    'description': """ 
        This module adds Warehouse to employee and related user.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr', 'stock'],
    'data': [
        'security/stock_security.xml',
        'views/hr_emplyee_views.xml',
        'views/res_user_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
