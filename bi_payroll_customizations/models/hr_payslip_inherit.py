# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def action_payslip_done(self):
        result = super(HrPayslip, self).action_payslip_done()
        if self.contract_id.analytic_account_id and self.move_id:
            for line in self.move_id.line_ids:
                line.write({'analytic_account_id': self.contract_id.analytic_account_id.id,
                            'name': line.name + ' / ' + self.employee_id.name})
        return result
