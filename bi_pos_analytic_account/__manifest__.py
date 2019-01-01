# -*- coding: utf-8 -*-
{
    'name': "BI POS Analytic Account",
    'summary': "BI POS Analytic Account",
    'description': """ 
        This module adds the analytic account to pos entries and set entry date to be the po date.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Point Of Sale',
    'version': '0.1',
    'depends': ['analytic', 'point_of_sale'],
    'data': [
        'views/point_of_sale_views.xml',
        'views/pos_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
