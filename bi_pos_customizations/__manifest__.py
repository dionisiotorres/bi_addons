# -*- coding: utf-8 -*-
{
    'name': "BI POS Customization",
    'summary': "BI POS Customization",
    'description': """ 
        This module allows the manual import of pos orders.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Point Of Sale',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
