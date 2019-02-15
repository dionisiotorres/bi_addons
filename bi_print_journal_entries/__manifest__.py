# -*- coding: utf-8 -*-
{
    'name': "BI Print Journal Entry Reports",
    'summary': "BI journal entry reports",
    'description': """ 
            This module prints Journal Entries as PDF report.
     """,
    'author': "BI Solutions Development Team",
    'category': 'accounting',
    'version': '0.1',
    'depends': ['base', 'account'],
    'data': [
        'views/report_journal_entry.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
