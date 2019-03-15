# -*- coding: utf-8 -*-
{
    'name': "Hr Reports",
    'summary': "Hr Reports",
    'author': "Bi Solution Team",
    'description': """Add reports to HR""",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['report_xlsx', 'hr', 'hr_payroll'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/payslip_report_wizard.xml",
        "reports/hr_payslips_report_view.xml",

        "views/menu_items_view.xml",
    ],
    'installable': True,
    'auto_install': False,
}
