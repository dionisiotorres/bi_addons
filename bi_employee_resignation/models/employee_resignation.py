# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeeResignation(models.Model):
    _name = 'employee.resignation'
    _inherit = ['mail.thread', 'resource.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id',
                                    readonly=1)
    warehouse_id = fields.Many2one('stock.warehouse', string='Branch', related='employee_id.warehouse_id', readonly=1)
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', readonly=1)
    employee_number = fields.Char(string='Employee Number', related='employee_id.employee_number', readonly=1)

    resignation_date = fields.Date(string='Resignation Date', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise ValidationError(_('You cannot delete confirmed employee resignation.'))
        return super(EmployeeResignation, self).unlink()

    @api.multi
    def set_state_to_confirmed(self):
        for rec in self:
            rec.state = 'confirmed'

    @api.multi
    def set_state_to_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'

    @api.multi
    def set_state_to_draft(self):
        for rec in self:
            rec.state = 'draft'
