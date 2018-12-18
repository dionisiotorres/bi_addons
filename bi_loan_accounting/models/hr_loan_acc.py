# -*- coding: utf-8 -*-
import time
from odoo import models, fields, api
from odoo.exceptions import except_orm


class HrLoanAcc(models.Model):
    _inherit = 'hr.loan'

    def _get_default_emp_account(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('bi_loan_accounting.loan_emp_account_id')) or False

    def _get_default_treasury_account(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('bi_loan_accounting.loan_treasury_account_id')) or False

    def _get_default_journal(self):
        return int(self.env['ir.config_parameter'].sudo().get_param('bi_loan_accounting.loan_journal_id')) or False

    @api.multi
    def _get_loan_lines_state(self):
        for loan in self:
            ready = False
            for line in loan.loan_lines:
                if not line.paid:
                    ready = True
            loan.is_loan_lines_ready = ready


    emp_account_id = fields.Many2one('account.account', string="Loan Account", default=_get_default_emp_account)
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account", default=_get_default_treasury_account)
    journal_id = fields.Many2one('account.journal', string="Journal", default=_get_default_journal)
    is_loan_lines_ready = fields.Boolean(string="Loan Lines Ready", compute='_get_loan_lines_state')

    @api.multi
    def action_approve(self):
        """This create account move for request.
            """
        loan_approve = self.env['ir.config_parameter'].sudo().get_param('account.loan_approve')
        contract_obj = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
        if not contract_obj:
            raise except_orm('Warning', 'You must Define a contract for employee')
        if not self.loan_lines:
            raise except_orm('Warning', 'You must compute installment before Approved')
        if loan_approve:
            self.write({'state': 'waiting_approval_2'})
        else:
            if not self.emp_account_id or not self.treasury_account_id or not self.journal_id:
                raise except_orm('Warning',
                                 "You must enter employee account & Treasury account and journal to approve ")
            if not self.loan_lines:
                raise except_orm('Warning', 'You must compute Loan Request before Approved')

            # old implementation to create account moves
            # timenow = time.strftime('%Y-%m-%d')
            # for loan in self:
            #     amount = loan.loan_amount
            #     loan_name = loan.employee_id.name
            #     reference = loan.name
            #     journal_id = loan.journal_id.id
            #     debit_account_id = loan.treasury_account_id.id
            #     credit_account_id = loan.emp_account_id.id
            #     debit_vals = {
            #         'name': loan_name,
            #         'account_id': debit_account_id,
            #         'journal_id': journal_id,
            #         'date': timenow,
            #         'debit': amount > 0.0 and amount or 0.0,
            #         'credit': amount < 0.0 and -amount or 0.0,
            #         'loan_id': loan.id,
            #     }
            #     credit_vals = {
            #         'name': loan_name,
            #         'account_id': credit_account_id,
            #         'journal_id': journal_id,
            #         'date': timenow,
            #         'debit': amount < 0.0 and -amount or 0.0,
            #         'credit': amount > 0.0 and amount or 0.0,
            #         'loan_id': loan.id,
            #     }
            #     vals = {
            #         'name': 'Loan For' + ' ' + loan_name,
            #         'narration': loan_name,
            #         'ref': reference,
            #         'journal_id': journal_id,
            #         'date': timenow,
            #         'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            #     }
            #     move = self.env['account.move'].create(vals)
            #     move.post()
            self.write({'state': 'approve'})
        return True

    @api.multi
    def action_double_approve(self):
        """This create account move for request in case of double approval.
            """
        if not self.emp_account_id or not self.treasury_account_id or not self.journal_id:
            raise except_orm('Warning', "You must enter employee account & Treasury account and journal to approve ")
        if not self.loan_lines:
            raise except_orm('Warning', 'You must compute Loan Request before Approved')

        # old implementation to create account moves
        # timenow = time.strftime('%Y-%m-%d')
        # for loan in self:
        #     amount = loan.loan_amount
        #     loan_name = loan.employee_id.name
        #     reference = loan.name
        #     journal_id = loan.journal_id.id
        #     debit_account_id = loan.treasury_account_id.id
        #     credit_account_id = loan.emp_account_id.id
        #     debit_vals = {
        #         'name': loan_name,
        #         'account_id': debit_account_id,
        #         'journal_id': journal_id,
        #         'date': timenow,
        #         'debit': amount > 0.0 and amount or 0.0,
        #         'credit': amount < 0.0 and -amount or 0.0,
        #         'loan_id': loan.id,
        #     }
        #     credit_vals = {
        #         'name': loan_name,
        #         'account_id': credit_account_id,
        #         'journal_id': journal_id,
        #         'date': timenow,
        #         'debit': amount < 0.0 and -amount or 0.0,
        #         'credit': amount > 0.0 and amount or 0.0,
        #         'loan_id': loan.id,
        #     }
        #     vals = {
        #         'name': 'Loan For' + ' ' + loan_name,
        #         'narration': loan_name,
        #         'ref': reference,
        #         'journal_id': journal_id,
        #         'date': timenow,
        #         'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        #     }
        #     move = self.env['account.move'].create(vals)
        #     move.post()
        self.write({'state': 'approve'})
        return True


class HrLoanLineAcc(models.Model):
    _inherit = "hr.loan.line"

    @api.one
    def action_paid_amount(self):
        """This create the account move line for payment of each installment.
            """
        timenow = time.strftime('%Y-%m-%d')
        for line in self:
            if line.loan_id.state != 'approve':
                raise except_orm('Warning', "Loan Request must be approved")
            amount = line.amount
            loan_name = line.employee_id.name
            reference = line.loan_id.name
            journal_id = line.loan_id.journal_id.id
            debit_account_id = line.loan_id.emp_account_id.id
            credit_account_id = line.loan_id.treasury_account_id.id
            debit_vals = {
                'name': loan_name,
                'account_id': debit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': loan_name,
                'account_id': credit_account_id,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                'name': 'Loan For' + ' ' + loan_name,
                'narration': loan_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)

            # leave it draft
            # move.post()
        return True

    @api.multi
    def make_payment(self):
        for rec in self:
            rec.action_paid_amount()
            rec.paid = True


class HrPayslipAcc(models.Model):
    _inherit = 'hr.payslip'

    # to generate entries for each loan line
    # @api.multi
    # def action_payslip_done(self):
    #     for line in self.input_line_ids:
    #         if line.loan_line_id:
    #             line.loan_line_id.action_paid_amount()
    #     return super(HrPayslipAcc, self).action_payslip_done()
