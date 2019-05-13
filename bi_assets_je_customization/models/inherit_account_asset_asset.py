# -*- coding: utf-8 -*-

from odoo import models, fields, api, _



class CreateNewJE(models.Model):
    _inherit = 'account.asset.asset'

    entry_related = fields.Many2one("account.move")

    @api.multi
    def asset_reconcile(self):
        journal_id = self.env['account.journal'].search([('name', '=', 'Asset Reconcile'), ('code', '=', 'AR')])
        # to_open_journal.action_date_assign()
        if not journal_id:
            raise Warning("Please Create the asset reconcile journal.")

        to_open_journal = self.env['account.move'].create({
            "name": self.name,
            "date": self.date,
            "journal_id": journal_id.id,
            "line_ids": [
                (0, 0, {
                            "account_id": journal_id.default_credit_account_id.id,
                            "date_maturity": 0,
                            "credit": self.value,
                            "debit": 0
                }),
                (0, 0, {
                            "account_id": journal_id.default_debit_account_id.id,
                            "date_maturity": 0,
                            "debit": self.value,
                            "credit": 0
                })
            ]
        })
        self.write({"entry_related": to_open_journal.id})

    @api.multi
    def open_journal_entries(self):
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'res_id': self.entry_related.id,
            'type': 'ir.actions.act_window',
        }

    accu_depreciation = fields.Float(string="Accumulated Depreciation", compute="_total_depreciation")

    @api.depends('value_residual', 'value')
    def _total_depreciation(self):
        for line in self:
            line.accu_depreciation = line.value - line.value_residual