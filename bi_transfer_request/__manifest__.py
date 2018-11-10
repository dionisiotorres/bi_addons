# -*- coding: utf-8 -*-
{
    'name': "BI Transfer Request",
    'summary': "BI Transfer Request",
    'description': """ 
            This module add transfer request to inventory.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['stock_account', 'hr'],
    'data': [
        'security/bi_transfer_request_security_view.xml',
        'security/ir.model.access.csv',
        # views
        'views/transfer_request_view.xml',
        'views/menu_item_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
