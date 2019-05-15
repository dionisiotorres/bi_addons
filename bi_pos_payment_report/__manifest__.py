# -*- coding: utf-8 -*-
{
    'name': "BI POS Payment Report",
    'summary': "BI POS Payment Report",
    'description': """ 
        This module adds new report for analyzing pos orders with payments.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Point Of Sale',
    'version': '0.1',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/point_of_sale_security.xml',
        'views/pos_order_payment_report_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
