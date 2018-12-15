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

    @api.model
    def create(self, vals):
        employee_object = self.env['hr.employee'].browse(vals['employee_id'])
        # send mail and notification to employee direct manager
        message = '<p>%s</p>' % _('New employee resignation created for %s and need your confirmation' % employee_object.name)
        # send email to hr manager to confirm move order
        self.env['mail.thread'].message_post(
            body=message,
            partner_ids=[employee_object.parent_id.user_id.partner_id.id],
        )
        # send notification to hr manager to confirm move order
        self.env['mail.thread'].message_post(
            body=message,
            subtype='mt_comment',
            message_type='comment',
            partner_ids=[(4,employee_object.parent_id.user_id.partner_id.id)],
        )

        return super(EmployeeResignation, self).create(vals)

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

            # send mail and notification to hr manager
            all_users = self.env['res.users'].search([])
            user_partner_ids = [user.partner_id.id for user in all_users if user.has_group('hr.group_hr_manager')]
            message_user_partner_ids = [(4, user.partner_id.id) for user in all_users if
                                        user.has_group('hr.group_hr_manager')]
            message = '<p>%s</p>' % _(
                'Employee resignation confirmed for %s and need to validate' % rec.employee_id.name)
            # send email to hr manager to confirm move order
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=user_partner_ids,
            )
            # send notification to hr manager to confirm move order
            self.env['mail.thread'].message_post(
                body=message,
                subtype='mt_comment',
                message_type='comment',
                partner_ids=message_user_partner_ids,
            )
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
