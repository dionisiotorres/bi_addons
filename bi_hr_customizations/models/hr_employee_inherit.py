# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class EmployeeCourse(models.Model):
    _name = 'employee.course'

    name = fields.Char(string='Name', required=True)


class EmployeeChild(models.Model):
    _name = 'employee.child'

    name = fields.Char(string='Name', required=True)
    age = fields.Float(string='Age')
    employee_id = fields.Many2one('hr.employee', string='Employee')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    passport_expiry_date = fields.Date(string='Passport Expiry Date')
    iqama_start_date = fields.Date(string='Iqama Start Date')
    iqama_expiry_date = fields.Date(string='Iqama Expiry Date')
    use_municipality_card = fields.Boolean(string='Use Municipality Card')
    mc_start_date = fields.Date(string='MC Start Date')
    mc_expiry_date = fields.Date(string='MC Expiry Date')
    employee_child_ids = fields.One2many('employee.child', 'employee_id', string='Childs')
    employee_number = fields.Char(string='Employee Number')
    employee_course_ids = fields.Many2many('employee.course',string='Employee Courses')
    account_asset_id = fields.Many2one('account.asset.asset',string='Employee Linked Asset')

    @api.multi
    @api.constrains('iqama_start_date', 'iqama_expiry_date', 'mc_start_date', 'mc_expiry_date')
    def check_dates(self):
        for rec in self:
            if rec.iqama_start_date > rec.iqama_expiry_date:
                raise ValidationError(_('Iqama start date must be less than iqama expiry date.'))

            if rec.mc_start_date > rec.mc_expiry_date:
                raise ValidationError(_('MC start date must be less than mc expiry date.'))
