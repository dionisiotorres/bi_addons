# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError, UserError
from odoo import models, api, _
import datetime


class EmployeesPayslipReportXls(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.bi_hr_reports.hr_payslips_report_xls'

    @api.model
    def generate_xlsx_report(self, workbook, data, wizard):
        worksheet = workbook.add_worksheet("PaySlip Report")
        row_no = 0
        col_no = 0

        f1 = workbook.add_format({'bold': True, 'font_color': 'black', })
        blue = workbook.add_format({'bold': True, 'font_color': 'blue', })
        gray = workbook.add_format({'bold': True, 'font_color': 'gray', })
        red = workbook.add_format({'bold': True, 'font_color': 'red', })
        green = workbook.add_format({'bold': True, 'font_color': 'green', })

        worksheet.write(row_no, col_no, 'Payslips Report', f1)
        worksheet.write(row_no, col_no + 1, wizard.company_id.name, )

        row_no += 2

        worksheet.write(row_no, col_no, 'From Date : ', f1)
        worksheet.write(row_no, col_no + 1, str(wizard.date_from), )
        row_no += 1
        worksheet.write(row_no, col_no, 'From To : ', f1)
        worksheet.write(row_no, col_no + 1, str(wizard.date_to), )
        row_no += 1
        worksheet.write(row_no, col_no, 'Departments : ', f1)

        if wizard.department_ids:
            worksheet.merge_range('B5:Z5', ", ".join(str(x) for x in wizard.department_ids.mapped('name')))
        else:
            worksheet.merge_range('B5:Z5', "All Departments")
        row_no += 1

        worksheet.write(row_no, col_no, 'Analytic  Accounts : ', f1)
        if wizard.analytic_account_ids:
            worksheet.merge_range('B6:Z6', ", ".join(str(x) for x in wizard.analytic_account_ids.mapped('name')))
        else:
            worksheet.merge_range('B6:Z6', "All Analytic Accounts")

        row_no += 3

        # Header Of Table Data
        worksheet.write(row_no, col_no, "Bank Account", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Employee Name", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Department", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "PaySlip / State ", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Salary Structure", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Analytic Account", f1)
        col_no += 1

        # End Of Header Table Data
        rules_domain = [('appears_on_payslip', '=', True), ('active', '=', True)]

        if wizard.rules_ids:
            rules_domain = [('id', 'in', wizard.rules_ids.ids)]

        rules_objs = self.env['hr.salary.rule'].search(rules_domain, order='sequence asc')

        payslip_domain = [('date_from', '>=', wizard.date_from), ('date_to', '<=', wizard.date_to),
                          ('company_id', '=', wizard.company_id.id)]

        if wizard.department_ids:
            payslip_domain.append(('employee_id.department_id', 'in', wizard.department_ids.ids))

        if wizard.analytic_account_ids:
            payslip_domain.append(('contract_id.analytic_account_id', 'in', wizard.analytic_account_ids.ids))

        if wizard.salary_struct_ids:
            payslip_domain.append(('struct_id', 'in', wizard.salary_struct_ids.ids))

        # TODO State domain
        if wizard.state == 'done_and_draft':
            payslip_domain.append(('state', 'in', ['draft', 'done']))

        else:
            payslip_domain.append(('state', '=', wizard.state))

        payslip_objs = self.env['hr.payslip'].search(payslip_domain, order='employee_id asc')

        footer_row = 0

        if wizard.group_by == 'salary_rules':
            for rule in rules_objs:
                rule_row = 8
                lines_domain = [('salary_rule_id', '=', rule.id), ('slip_id.date_from', '>=', wizard.date_from),
                                ('slip_id.company_id', '>=', wizard.company_id.id),
                                ('slip_id.date_to', '<=', wizard.date_to)]

                if wizard.salary_struct_ids:
                    lines_domain.append(('slip_id.struct_id', 'in', wizard.salary_struct_ids.ids))

                if wizard.analytic_account_ids:
                    lines_domain.append(('contract_id.analytic_account_id', 'in', wizard.analytic_account_ids.ids))

                if wizard.department_ids:
                    lines_domain.append(('slip_id.employee_id.department_id', 'in', wizard.department_ids.ids))

                if wizard.state == 'done_and_draft':
                    lines_domain.append(('slip_id.state', 'in', ['draft', 'done']))
                else:
                    lines_domain.append(('slip_id.state', '=', wizard.state))

                lines_objs = self.env['hr.payslip.line'].search(lines_domain)

                worksheet.write(rule_row, col_no, rule.name, green)

                for payslip in payslip_objs:
                    rule_row += 1
                    worksheet.write(rule_row, 0, payslip.employee_id.bank_account_id.acc_number or " " + " - " + str(
                        payslip.employee_id.bank_account_id.bank_id.name or ' '))
                    worksheet.write(rule_row, 1, payslip.employee_id.name)
                    worksheet.write(rule_row, 2, payslip.employee_id.department_id.name or ' ')
                    worksheet.write(rule_row, 3, str(payslip.number or ' ') + " / " + str(payslip.state.capitalize()))
                    worksheet.write(rule_row, 4, payslip.struct_id.name)
                    worksheet.write(rule_row, 5, payslip.contract_id.analytic_account_id.name or ' ')

                    for line in payslip.line_ids:
                        if line.salary_rule_id.id == rule.id:
                            worksheet.write(rule_row, col_no, line.total)

                if footer_row < rule_row:
                    footer_row = rule_row

                # TODO SUM Per Salary Rule
                total_rule_amount = sum(lines.total for lines in lines_objs)
                worksheet.write(footer_row + 2, col_no, total_rule_amount, blue)
                col_no += 1

            worksheet.write(footer_row + 2, 5, "Total", red)

        elif wizard.group_by == 'salary_categories':
            rules_categ_objs = self.env['hr.salary.rule.category'].search([], order='sequence asc')
            for category in rules_categ_objs:
                rule_row = 8
                lines_domain = [('salary_rule_id.category_id', '=', category.id),
                                ('slip_id.date_from', '>=', wizard.date_from),
                                ('slip_id.company_id', '>=', wizard.company_id.id),
                                ('slip_id.date_to', '<=', wizard.date_to)]

                if wizard.analytic_account_ids:
                    lines_domain.append(('contract_id.analytic_account_id', 'in', wizard.analytic_account_ids.ids))

                if wizard.department_ids:
                    lines_domain.append(('slip_id.employee_id.department_id', 'in', wizard.department_ids.ids))

                if wizard.salary_struct_ids:
                    lines_domain.append(('slip_id.struct_id', 'in', wizard.salary_struct_ids.ids))

                if wizard.state == 'done_and_draft':
                    lines_domain.append(('slip_id.state', 'in', ['draft', 'done']))
                else:
                    lines_domain.append(('slip_id.state', '=', wizard.state))

                lines_objs = self.env['hr.payslip.line'].search(lines_domain)
                worksheet.write(rule_row, col_no, category.name, green)

                for payslip in payslip_objs:
                    rule_row += 1
                    worksheet.write(rule_row, 0, payslip.employee_id.bank_account_id.acc_number or " " + " - " + str(
                        payslip.employee_id.bank_account_id.bank_id.name or ' '))
                    worksheet.write(rule_row, 1, payslip.employee_id.name)
                    worksheet.write(rule_row, 2, payslip.employee_id.department_id.name or ' ')
                    worksheet.write(rule_row, 3, str(payslip.number or ' ') + " / " + str(payslip.state.capitalize()))
                    worksheet.write(rule_row, 4, payslip.struct_id.name)
                    worksheet.write(rule_row, 5, payslip.contract_id.analytic_account_id.name or ' ')

                    total_categ = 0.0
                    for line in payslip.line_ids:
                        if line.salary_rule_id.category_id.id == category.id:
                            total_categ += line.total
                    worksheet.write(rule_row, col_no, total_categ)

                if footer_row < rule_row:
                    footer_row = rule_row

                # TODO SUM Per Salary Rules Category
                total_rule_categ_amount = sum(lines.total for lines in lines_objs)
                worksheet.write(footer_row + 2, col_no, total_rule_categ_amount, blue)
                col_no += 1
            worksheet.write(footer_row + 2, 5, "Total", red)
