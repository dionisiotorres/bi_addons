# -*- coding: utf-8 -*-
{
    'name': 'Bi Purchase Request Inherit',
    'summary': 'Bi Purchase Request Inherit',
    'version': '1.0',

    'website': 'https://www.centione.com',
    'depends': ['purchase', 'purchase_request', 'purchase_request_to_rfq', 'hr', 'bi_employee_warehouse'],
    'data': [
        'security/purchase_request_inherit_security_view.xml',
        'security/ir.model.access.csv',
        'views/purchase_request_inherit_view.xml',
        'views/purchase_order_inherit_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
