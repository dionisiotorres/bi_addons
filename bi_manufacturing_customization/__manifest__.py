# -*- coding: utf-8 -*-
{
    'name': "BI Manufacturing Customization",
    'summary': "BI Manufacturing Customization",
    'description': """ 
            This module adds ruq and wq columns to manufacturing module, and retrieve their quantities in mos.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Manufacturing',
    'version': '0.1',
    'depends': ['stock_account', 'mrp'],
    'data': [
        'views/mrp_bom_line_inherit_view.xml',
        'views/mrp_production_inherit_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
