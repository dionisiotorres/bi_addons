# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError, UserError
from odoo import models, api, _
import datetime


class EmployeesPayslipReportXls(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.bi_hr_reports.hr_payslips_report_xls'

    @api.model
    def generate_xlsx_report(self, workbook, data, wizard):
        worksheet = workbook.add_worksheet("Payslip Generic Report XLS")
        row_no = 0
        col_no = 0

        f1 = workbook.add_format({'bold': True, 'font_color': 'black', })
        blue = workbook.add_format({'bold': True, 'font_color': 'blue', })
        gray = workbook.add_format({'bold': True, 'font_color': 'gray', })
        red = workbook.add_format({'bold': True, 'font_color': 'red', })
        green = workbook.add_format({'bold': True, 'font_color': 'green', })

        worksheet.write(row_no, col_no, 'Payslips Report', f1)
        row_no += 2

        worksheet.write(row_no, col_no, 'From Date : ', f1)
        worksheet.write(row_no, col_no + 1, str(wizard.date_from), )
        row_no += 1
        worksheet.write(row_no, col_no, 'From To : ', f1)
        worksheet.write(row_no, col_no + 1, str(wizard.date_to), )
        row_no += 1
        worksheet.write(row_no, col_no, 'Report Date: ', f1)
        worksheet.write(row_no, col_no + 1, str(wizard.date_now), )
        row_no += 3

        # Header Of Table Data
        worksheet.write(row_no, col_no, "Bank Account", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Employee Name", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Department", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "PaySlip", f1)
        col_no += 1
        worksheet.write(row_no, col_no, "Salary Structure", f1)
        col_no += 1
        # End Of Header Table Data
        rules_objs = self.env['hr.salary.rule'].search([('appears_on_payslip', '=', True), ('active', '=', True)],
                                                       order='sequence asc')

        payslip_objs = self.env['hr.payslip'].search(
            [('state', '=', wizard.state), ('date_from', '>=', wizard.date_from), ('date_to', '<=', wizard.date_to),
             ('company_id', '=', wizard.company_id.id), '|',
             ('employee_id.department_id.id', 'in', wizard.department_ids.ids),
             ('employee_id.department_id', '=', False)],
            order='employee_id')

        footer_row = 0
        for rule in rules_objs:
            rule_row = 7
            lines_objs = self.env['hr.payslip.line'].search(
                [('salary_rule_id', '=', rule.id), ('slip_id.date_from', '>=', wizard.date_from),
                 ('slip_id.company_id', '>=', wizard.company_id.id),
                 ('slip_id.state', '=', wizard.state), ('slip_id.date_to', '<=', wizard.date_to)])

            worksheet.write(rule_row, col_no, rule.name, blue)

            for payslip in payslip_objs:
                rule_row += 1
                worksheet.write(rule_row, 0, payslip.employee_id.bank_account_id.acc_number or " " + " - " + str(
                    payslip.employee_id.bank_account_id.bank_id.name or ' '))
                worksheet.write(rule_row, 1, payslip.employee_id.name)
                worksheet.write(rule_row, 2, payslip.employee_id.department_id.name or ' ')
                worksheet.write(rule_row, 3, payslip.number)
                worksheet.write(rule_row, 4, payslip.struct_id.name)

                for line in payslip.line_ids:
                    if line.salary_rule_id.id == rule.id:
                        worksheet.write(rule_row, col_no, line.total)
                        if footer_row < rule_row:
                            footer_row = rule_row

            # TODO SUM Per Salary Rule
            total_rule_amount = sum(lines.total for lines in lines_objs)
            worksheet.write(footer_row + 2, col_no, total_rule_amount, green)
            col_no += 1
        worksheet.write(footer_row + 2, 3, "Total", red)
