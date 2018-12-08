# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeeStartWorkRequest(models.Model):
    _name = 'employee.start.work.request'
    _inherit = ['mail.thread', 'resource.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    country_id = fields.Many2one('res.country', string='Nationality (Country)', related='employee_id.country_id',
                                 readonly=1)
    identification_id = fields.Char(string='Identification No', related='employee_id.identification_id',
                                    readonly=1)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',
                                      related='employee_id.bank_account_id',
                                      readonly=1)
    start_work_date = fields.Date(string='Start Work At', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirmed':
                raise ValidationError(_('You cannot delete confirmed employee start work request.'))
        return super(EmployeeStartWorkRequest, self).unlink()

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
