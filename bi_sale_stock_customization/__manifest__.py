# -*- coding: utf-8 -*-
{
    'name': "BI Sale Stock Customization",
    'summary': "BI Sale Stock Customization",
    'description': """ 
            This module edit on sale to edit expected date in orders and it's shipments and pass effective date in pickings moves/entries.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Sale',
    'version': '0.1',
    'depends': ['base','stock','stock_account'],
    'data': [
        'views/stock_picking_inherit_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
