# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    sa_emp_account_id = fields.Many2one('account.account', string="Salary Advance Account")
    sa_treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    sa_journal_id = fields.Many2one('account.journal', string="Salary Advance Journal")

    @api.model
    def get_values(self):
        res = super(AccConfig, self).get_values()
        res.update(
            sa_emp_account_id=int(self.env['ir.config_parameter'].sudo().get_param('bi_salary_advance.sa_emp_account_id')),
            sa_treasury_account_id=int(self.env['ir.config_parameter'].sudo().get_param('bi_salary_advance.sa_treasury_account_id')),
            sa_journal_id=int(self.env['ir.config_parameter'].sudo().get_param('bi_salary_advance.sa_journal_id')),
        )
        return res

    @api.multi
    def set_values(self):
        super(AccConfig, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('bi_salary_advance.sa_emp_account_id', self.sa_emp_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('bi_salary_advance.sa_treasury_account_id', self.sa_treasury_account_id.id)
        self.env['ir.config_parameter'].sudo().set_param('bi_salary_advance.sa_journal_id', self.sa_journal_id.id)