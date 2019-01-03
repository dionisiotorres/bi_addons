# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountBankStatementInherit(models.Model):
    _inherit = 'account.bank.statement'

    pos_id = fields.Many2one('pos.config', related='pos_session_id.config_id', string='Point of sale', store=True)


class PosSessionStatementReportWizard(models.TransientModel):
    _name = 'pos.session.statement.report.wizard'

    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    date = fields.Date(string='Date', required=True, default=_get_default_date)


    @api.multi
    def open_session_statements(self):
        self.ensure_one()

        tree_view_ref = self.env.ref('bi_foodics_integration.account_bank_statement_tree_view', False)

        return  {
            'domain': [('pos_session_id.st_date', '=', self.date)],
            'name': 'Statements',
            'res_model': 'account.bank.statement',
            'type': 'ir.actions.act_window',
            'views': [(tree_view_ref.id, 'tree')],
        }