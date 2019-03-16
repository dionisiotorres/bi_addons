# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class PayslipWizardReport(models.TransientModel):
    _name = 'payslip.employee.wizard.report'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.id)

    date_from = fields.Date(string='Date From', )
    date_to = fields.Date(string='Date To', )
    department_ids = fields.Many2many('hr.department', string="Departments", required=True)
    state = fields.Selection([('done', 'Done'), ('verify', 'Waiting'), ('draft', 'Draft'), ], string="State",
                             default='done')
    select_rules = fields.Boolean('Select Rules')
    rules_ids = fields.Many2many('hr.salary.rule', string="Rules")

    @api.onchange('date_from')
    def get_date_to(self):
        for val in self:
            if val.date_from:
                val.date_to = ((datetime.strptime(str(val.date_from), '%Y-%m-%d').date() + relativedelta(
                    months=1)) - relativedelta(days=1))
            else:
                val.date_to = False

    @api.onchange('company_id')
    def get_department_ids(self):
        for val in self:
            val.rules_ids = False
            if val.company_id:

                department_ids = self.env['hr.department'].search(
                    ['|', ('company_id', '=', val.company_id.id), ('company_id', '=', False)])
                rules_ids = self.env['hr.salary.rule'].search(
                    ['|', ('company_id', '=', val.company_id.id), ('company_id', '=', False)])

                val.department_ids = department_ids.ids
            else:
                val.department_ids = False

        return {
            'domain': {
                'department_ids': [('id', 'in', department_ids.ids)],
                'rules_ids': [('id', 'in', rules_ids.ids)]
            }}

    @api.multi
    def get_payroll_data(self):
        data = self.read()[0]
        datas = {
            'ids': [],
            'model': 'hr.payslip',
            'form': data
        }
        payslip_objs = self.env['hr.payslip'].search([('state', '=', self.state), ('date_from', '>=', self.date_from),
                                                      ('date_to', '<=', self.date_to),
                                                      ('company_id', '=', self.company_id.id), '|',
                                                      ('employee_id.department_id.id', 'in', self.department_ids.ids),
                                                      ('employee_id.department_id', '=', False)])

        if not payslip_objs:
            raise ValidationError(_("Did not found record depends on your selection !!"))

        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'bi_hr_reports.hr_payslips_report_xls'),
             ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=datas)
