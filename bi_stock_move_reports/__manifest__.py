# -*- coding: utf-8 -*-
{
    'name': "BI Stock Move Reports",
    'summary': "BI Stock Move Reports",
    'description': """ 
        This module adds custom reports for stock moves.\n
        1- Total moves for products per location.
        2- Total moves for products per warehouse.
        3- Total moves for products per all company.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['product', 'stock', 'stock_account', 'report_xlsx'],
    'data': [
        'views/stock_move_views.xml',
        'wizard/stock_move_report_wizard.xml',
        'reports/total_move_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
