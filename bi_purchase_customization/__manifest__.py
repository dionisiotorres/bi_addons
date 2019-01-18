# -*- coding: utf-8 -*-
{
    'name': "BI Purchase Customization",
    'summary': "BI Purchase Customization",
    'description': """ 
            This module adds new field to purchase and PO report.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Purchase',
    'version': '0.1',
    'depends': ['stock', 'purchase', 'purchase_stock'],
    'data': [
        'views/purchase_order_inherit_view.xml',
        'reports/purchase_order_report_inherit_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
