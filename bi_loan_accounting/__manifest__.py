# -*- coding: utf-8 -*-
{
    'name': 'BI Loan Accounting',
    'version': '0.1',
    'summary': 'BI Loan Accounting',
    'description': """
        Create accounting entries for loan requests.
        """,
    'category': 'Human Resources',
    'author': "BI Solutions Development Team",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'bi_loan_management',
    ],
    'data': [
        'wizard/loan_payment_wizard.xml',
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
