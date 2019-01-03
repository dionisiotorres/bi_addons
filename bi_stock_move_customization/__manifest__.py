# -*- coding: utf-8 -*-
{
    'name': "BI Add Vendor to Stock",
    'summary': "BI Add Vendor to Stock",
    'description': """ 
            This module adds vendor to stock moves.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Stock',
    'version': '0.1',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_move_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
