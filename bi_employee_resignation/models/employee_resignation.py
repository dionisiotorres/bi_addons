# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeeResignation(models.Model):
    _name = 'employee.resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _description = "Employee Resignation Request"
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',
                                    readonly=1)
    warehouse_id = fields.Many2one('stock.warehouse', string='Branch', related='employee_id.warehouse_id', readonly=1)
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', readonly=1)
    employee_number = fields.Char(string='Employee Number', related='employee_id.employee_number', readonly=1)

    resignation_date = fields.Date(string='Resignation Date', required=True,translate=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'validated':
                raise ValidationError(_('You cannot delete validated employee resignation.'))
        return super(EmployeeResignation, self).unlink()

    @api.multi
    def set_state_to_confirmed(self):
        for rec in self:
            if self.env.uid != rec.employee_id.parent_id.user_id.id:
                raise ValidationError(_('only employee direct manager can confirm employee resignation.'))
            rec.state = 'confirmed'

    @api.multi
    def set_state_to_validated(self):
        for rec in self:
            rec.state = 'validated'

    @api.multi
    def set_state_to_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'

    @api.multi
    def set_state_to_draft(self):
        for rec in self:
            rec.state = 'draft'
