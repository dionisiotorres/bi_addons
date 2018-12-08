# -*- coding: utf-8 -*-
{
    'name': "BI HR Customizations",
    'summary': "BI HR Customizations",
    'description': """ 
        This module add fields to employee contract effect in payslip.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr_payroll', 'account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_salary_rules_data.xml',
        'views/hr_employee_inherit_view.xml',
        'views/hr_contract_inherit_view.xml',
        'views/employee_start_work_request_view.xml',
        'views/menu_item_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
