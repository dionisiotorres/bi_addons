# -*- coding: utf-8 -*-
{
    'name': 'BI Advance Salary',
    'version': '0.1',
    'summary': 'Advance Salary In HR',
    'description': """
        Helps you to manage Advance Salary Request of your company's staff.
        """,
    'category': 'Human Resources',
    'author': "BI Solutions Development Team",
    'depends': [
        'hr_payroll', 'hr', 'account', 'hr_contract', 'bi_loan_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_salary_advance_config.xml',
        'views/salary_structure.xml',
        'views/salary_advance.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
