# -*- coding: utf-8 -*-

from odoo import models


class JournalEntryReport(models.Model):
    _inherit = 'account.move'
    # _rec_name = 'analytic_account_id'


    def print_journal_entry(self):
        return self.env.ref('bi_print_journal_entries.action_report_journal_entry').report_action(self)