# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'
    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id):
        res = super(StockMoveInherit, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id,
                                       credit_account_id)
        if self._context.get('pos_analytic_account_id', False) and res.get('debit_line_vals', False):
            res['debit_line_vals'].update({
                'analytic_account_id': self._context.get('pos_analytic_account_id'),
            })
        return res