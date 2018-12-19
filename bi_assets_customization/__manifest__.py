# -*- coding: utf-8 -*-
{
    'name': "BI Asset Customization",
    'summary': "BI Asset Customization",
    'description': """ 
            This module adds new page to assets to explain track asset moves.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['resource', 'hr', 'account_asset'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_history_view.xml',
        'views/account_asset_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
