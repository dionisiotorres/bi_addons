# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LoanPaymentWizard(models.TransientModel):
    _name = 'loan.payment.wizard'

    loan_id = fields.Many2one('hr.loan', string="Loan Ref.")
    loan_lines_ids = fields.Many2many('hr.loan.line', string='Loan Lines')


    @api.onchange('loan_id')
    def onchange_loan(self):
        if self.loan_id:
            self.loan_lines_ids = self.loan_id.loan_lines.filtered(lambda x: not x.paid)

    @api.multi
    def make_payment(self):
        for rec in self:
            lines = rec.loan_id.loan_lines.filtered(lambda x: x in rec.loan_lines_ids)
            lines.make_payment()