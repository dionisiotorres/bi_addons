# -*- coding: utf-8 -*-
{
    'name': "BI Item Card Report",
    'summary': "BI Item Card Report",
    'description': """ 
        This module adds four reports for items(Products).\n
        1- Item Card.
        2- Item Card With Cost.
        3- Items With Totals.
        4- Items With Totals And Cost.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Inventory',
    'version': '0.1',
    'depends': ['stock'],
    'data': [
        'wizard/item_card_wizard_view.xml',
        'views/item_card_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
