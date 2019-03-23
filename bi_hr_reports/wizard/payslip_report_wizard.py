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
    department_ids = fields.Many2many('hr.department', string="Departments")
    state = fields.Selection(
        [('done_and_draft', 'Draft,Done'), ('done', 'Done'), ('draft', 'Draft'), ('verify', 'Waiting')],
        string="State", default='done_and_draft')
    salary_struct_ids = fields.Many2many('hr.payroll.structure', string='Salary Structures')
    group_by = fields.Selection([('salary_rules', 'Salary Rules'), ('salary_categories', 'Salary Categories')],
                                string="Group By", required=True, default='salary_categories')
    rules_ids = fields.Many2many('hr.salary.rule', string="Rules")
    categories_ids = fields.Many2many('hr.salary.rule.category', string="Categories")
    analytic_account_ids = fields.Many2many('account.analytic.account', string="Analytic Account")

    @api.onchange('categories_ids', 'group_by')
    def onchange_categories_ids(self):
        if self.categories_ids and (self.group_by == 'salary_categories'):
            self.rules_ids = self.env['hr.salary.rule'].search([('category_id', 'in', self.categories_ids.ids)])
        if not self.categories_ids:
            self.rules_ids = False

    @api.onchange('salary_struct_ids', 'group_by')
    def get_rules_ids(self):
        rules_ids = []
        categories_ids = []

        if self.salary_struct_ids and (self.group_by == 'salary_rules'):
            for struct in self.salary_struct_ids:
                for rule in struct.rule_ids:
                    if rule.id not in rules_ids:
                        rules_ids.append(rule.id)
            self.rules_ids = rules_ids
            return {
                'domain': {
                    'rules_ids': [('id', 'in', rules_ids)],
                }}

        if self.salary_struct_ids and (self.group_by == 'salary_categories'):
            for struct in self.salary_struct_ids:
                for rule in struct.rule_ids:
                    if (rule.category_id.id not in categories_ids) and rule.category_id.view_in_report:
                        categories_ids.append(rule.category_id.id)
            self.categories_ids = categories_ids
            return {
                'domain': {
                    'categories_ids': [('id', 'in', categories_ids)],
                }}
        else:
            self.rules_ids = False
            self.categories_ids = False
            return {
                'domain': {
                    'categories_ids': [('view_in_report', '=', True)],
                    'rules_ids': [],
                }}

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
            val.salary_struct_ids = False
            val.analytic_account_ids = False
            val.categories_ids = False
            if val.company_id:

                department_ids = self.env['hr.department'].search(
                    ['|', ('company_id', '=', val.company_id.id), ('company_id', '=', False)])
                rules_ids = self.env['hr.salary.rule'].search(
                    ['|', ('company_id', '=', val.company_id.id), ('company_id', '=', False)])
                struct_ids = self.env['hr.payroll.structure'].search(
                    ['|', ('company_id', '=', val.company_id.id), ('company_id', '=', False)])
                analytic_account_ids = self.env['account.analytic.account'].search(
                    ['|', ('company_id', '=', val.company_id.id), ('company_id', '=', False)])
                categories_ids = self.env['hr.salary.rule.category'].search([('view_in_report', '=', True)])
            else:
                val.department_ids = False

        return {
            'domain': {
                'department_ids': [('id', 'in', department_ids.ids)],
                'rules_ids': [('id', 'in', rules_ids.ids)],
                'salary_struct_ids': [('id', 'in', struct_ids.ids)],
                'analytic_account_ids': [('id', 'in', analytic_account_ids.ids)],
                'categories_ids': [('id', 'in', categories_ids.ids)]
            }}

    @api.multi
    def get_payroll_data(self):
        data = self.read()[0]
        datas = {
            'ids': [],
            'model': 'hr.payslip',
            'form': data
        }
        domain = [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to),
                  ('company_id', '=', self.company_id.id)]

        if self.department_ids:
            domain.append(('employee_id.department_id', 'in', self.department_ids.ids))

        if self.salary_struct_ids:
            domain.append(('struct_id', 'in', self.salary_struct_ids.ids))

        if self.analytic_account_ids:
            domain.append(('contract_id.analytic_account_id', 'in', self.analytic_account_ids.ids))

        if self.state == 'done_and_draft':
            domain.append(('state', 'in', ['draft', 'done']))
        else:
            domain.append(('state', '=', self.state))

        payslip_objs = self.env['hr.payslip'].search(domain)

        if not payslip_objs:
            raise ValidationError(_("Did not found record depends on your selection !!"))

        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'bi_hr_reports.hr_payslips_report_xls'),
             ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=datas)
