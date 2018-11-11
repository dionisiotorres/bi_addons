# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TransferRequest(models.Model):
    _name = 'transfer.request'
    _inherit = ['mail.thread', 'resource.mixin']

    name = fields.Char(string='Name', readonly=1)
    requested_by_employee_id = fields.Many2one('hr.employee', string='Requester')
    requested_for_employee_id = fields.Many2one('hr.employee', string='Requested For')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', )
    cancel_reason = fields.Html(string='Cancel Reason')
    transfer_request_line_ids = fields.One2many('transfer.request.line', 'transfer_request_id',
                                                string='Transferred Products')
    source_stock_location_id = fields.Many2one('stock.location', string='Source Location', )
    destination_stock_location_id = fields.Many2one('stock.location', string='Destination Location',
                                                    domain=[('usage', '=', 'transit')])
    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve'), ('transferring', 'Transferring'), ('done', 'Done'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('transfer.request')
        return super(TransferRequest, self).create(vals)

    @api.multi
    def unlink(self):
        for appointment in self:
            if appointment.state == 'done':
                raise ValidationError(_('You cannot delete done transfer request.'))
        return super(TransferRequest, self).unlink()

    @api.multi
    def set_state_to_approve(self):
        for rec in self:
            rec.state = 'approve'

    @api.multi
    def set_state_to_cancelled(self):
        for rec in self:
            if not rec.cancel_reason:
                raise ValidationError(_('Please add reason for cancel request first.'))
            rec.state = 'cancelled'

    @api.multi
    def set_state_to_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.multi
    def set_state_to_transferring(self):
        for rec in self:
            rec.state = 'transferring'

    @api.multi
    def set_state_to_done(self):
        for rec in self:
            rec.state = 'done'


class TransferRequestLine(models.Model):
    _name = 'transfer.request.line'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    transfer_request_id = fields.Many2one('transfer.request', string='Transfer Request')
    transferred_qty = fields.Float(string='Transferred Qty', )
    transfer_created = fields.Boolean(string='Transfer Created')
    qty = fields.Float(string='Qty', required=True, default=1.0)
    notes = fields.Char(string='Notes')
    product_uom_id = fields.Many2one('product.uom', string='UoM',
                                     required=True)

    @api.onchange('product_id')
    def default_fields(self):
        for line in self:
            if line.product_id:
                line.product_uom_id = line.product_id.uom_id.id
