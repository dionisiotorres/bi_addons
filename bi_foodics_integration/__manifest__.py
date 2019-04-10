# -*- coding: utf-8 -*-
{
    'name': "BI Foodics Integration",
    'summary': "BI Foodics Integration",
    'description': """ 
            This module adds the Foodics API integration.
     """,
    'author': "BI Solutions Development Team",
    'category': '',
    'version': '0.1',
    'depends': ['point_of_sale', 'account', 'product', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_foodics_wizard.xml',
        'wizard/pos_session_statement_report_wizard.xml',
        'data/data.xml',
        'views/pos_res_config_settings_views.xml',
        'views/pos_branch_views.xml',
        'views/point_of_sale_views_inherit.xml',
        'views/account_journal_views_inherit.xml',
        'views/account_tax_views_inherit.xml',
        'views/res_partner_views_inherit.xml',
        'views/res_users_views_inherit.xml',
        'views/product_views_inherit.xml',
        'views/api_import_exception_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
