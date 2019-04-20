# -*- coding: utf-8 -*-
{
    'name': "Bi Account Customization",
    'summary': "Bi Account Customization",
    'description': """
    """,
    'author': "BI Solutions Development Team",
    'category': 'accounting',
    'version': '0.1',
    'depends': ['base', 'account', 'sale_management', 'account_accountant', 'stock', 'stock_account'],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 44
}
