# -*- coding: utf-8 -*-
{
    'name': "BI Assets - JE Customization",
    'summary': "BI customize JE with specific values",
    'description': """ 
            This module creates new JE after assets confirmation with specific values.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account_accountant', 'base'],
    'data': [
        'views/inherit_account_asset_asset_view.xml',
        'views/inherit_account_journal_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
