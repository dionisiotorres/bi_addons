# -*- coding: utf-8 -*-
{
    'name': "BI Inventory Customization",
    'summary': "BI Inventory Customization",
    'description': """ 
        This module modify in inventory module.
     """,
    'author': "BI Solutions Development Team",
    'category': 'Warehouse',
    'version': '0.1',
    'depends': ['bi_employee_warehouse', 'account', 'stock','product', 'stock_account', 'sale_stock'],
    'data': [
        'security/bi_inventory_customization_security_view.xml',
        'views/stock_picking_inherit_view.xml',
        'views/stock_scrap_inherit_view.xml',
        'views/stock_quant_inherit_view.xml',
        'views/product_inherit_view.xml',
        'views/stock_quantity_history_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
