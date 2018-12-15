from odoo import models, fields, api, _


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    loan_approve = fields.Boolean(default=False, string="Approval from Accounting Department",
                                  help="Loan Approval from account manager")
    loan_emp_account_id = fields.Many2one('account.account', string="Loan Account")
    loan_treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    loan_journal_id = fields.Many2one('account.journal', string="Loan Journal")

    @api.model
    def get_values(self):
        res = super(AccConfig, self).get_values()
        res.update(
            loan_approve=self.env['ir.config_parameter'].sudo().get_param('account.loan_approve'),
            loan_emp_account_id=int(self.env['ir.config_parameter'].sudo().get_param('bi_loan_accounting.loan_emp_account_id')),
            loan_treasury_account_id=int(self.env['ir.config_parameter'].sudo().get_param('bi_loan_accounting.loan_treasury_account_id')),
            loan_journal_id=int(self.env['ir.config_parameter'].sudo().get_param('bi_loan_accounting.loan_journal_id')),
        )
        return res

    @api.multi
    def set_values(self):
        super(AccConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('account.loan_approve', self.loan_approve)
        self.env['ir.config_parameter'].sudo().set_param('bi_loan_accounting.loan_emp_account_id', self.loan_emp_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('bi_loan_accounting.loan_treasury_account_id', self.loan_treasury_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('bi_loan_accounting.loan_journal_id', self.loan_journal_id.id)