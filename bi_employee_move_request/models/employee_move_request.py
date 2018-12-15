# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EmployeeMoveReason(models.Model):
    _name = 'employee.move.reason'

    name = fields.Char(string='Name', required=True, translate=True)


class EmployeeMoveRequest(models.Model):
    _name = 'employee.move.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']
    _description = "Employee Move Request"

    name = fields.Char(string='Name', readonly=True)
    request_date = fields.Date(string='Transfer Date', required=True, translate=True)
    employee_move_reason_id = fields.Many2one('employee.move.reason', string='Transfer Reason', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validated', 'Validated'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')
    employee_department_id = fields.Many2one('hr.department', string='Department', compute='get_employee_data',
                                             store=True)
    employee_analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                                   compute='get_employee_data',
                                                   store=True)
    employee_warehouse_id = fields.Many2one('stock.warehouse', string='Branch', compute='get_employee_data',
                                            store=True)

    department_id = fields.Many2one('hr.department', string='New Department', )
    analytic_account_id = fields.Many2one('account.analytic.account', string='New Analytic Account', )
    warehouse_id = fields.Many2one('stock.warehouse', string='New Branch')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.move.request')
        employee_object = self.env['hr.employee'].browse(vals['employee_id'])

        # send mail and notification to hr manager
        all_users = self.env['res.users'].search([])
        user_partner_ids = [user.partner_id.id for user in all_users if user.has_group('hr.group_hr_manager')]
        message_user_partner_ids = [(4, user.partner_id.id) for user in all_users if user.has_group('hr.group_hr_manager')]
        message = '<p>%s</p>' % _('New move request created for %s and need your confirmation' % employee_object.name)
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

        return super(EmployeeMoveRequest, self).create(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'validated':
                raise ValidationError(_('You cannot delete validated move request.'))
        return super(EmployeeMoveRequest, self).unlink()

    @api.multi
    @api.depends('employee_id')
    def get_employee_data(self):
        for rec in self:
            rec.employee_department_id = rec.employee_id.department_id.id
            rec.employee_analytic_account_id = rec.employee_id.contract_id.analytic_account_id.id
            rec.employee_warehouse_id = rec.employee_id.warehouse_id.id

    @api.multi
    def set_state_to_confirmed(self):
        for rec in self:
            # send mail and notification to accounting manager to validate
            all_users = self.env['res.users'].search([])
            user_partner_ids = [user.partner_id.id for user in all_users if user.has_group('account.group_account_manager')]
            message_user_partner_ids = [(4, user.partner_id.id) for user in all_users if
                                        user.has_group('account.group_account_manager')]
            message = '<p>%s</p>' % _(
                'Move request confirmed for %s and need to validate' % rec.employee_id.name)
            # send email to accounting manager to validate move order
            self.env['mail.thread'].message_post(
                body=message,
                partner_ids=user_partner_ids,
            )
            # send notification to accounting  manager to validate move order
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
            rec.employee_id.write({
                'department_id': rec.department_id.id,
                'warehouse_id': rec.warehouse_id.id
            })
            if rec.employee_id.contract_id:
                rec.employee_id.contract_id.write({
                    'analytic_account_id': rec.analytic_account_id.id,
                })

    @api.multi
    def set_state_to_cancelled(self):
        for rec in self:
            rec.state = 'cancelled'

    @api.multi
    def set_state_to_draft(self):
        for rec in self:
            rec.state = 'draft'
