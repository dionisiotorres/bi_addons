# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer_request_id = fields.Many2one('transfer.request', string='Transfer Request')


class TransferRequest(models.Model):
    _name = 'transfer.request'
    _inherit = ['mail.thread', 'resource.mixin']

    name = fields.Char(string='Name', readonly=1)
    requested_by_employee_id = fields.Many2one('hr.employee', string='Requester')
    requested_for_employee_id = fields.Many2one('hr.employee', string='Requested For')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', )
    cancel_reason = fields.Html(string='Cancellation Reason')
    transfer_request_line_ids = fields.One2many('transfer.request.line', 'transfer_request_id',
                                                string='Transferred Products')
    source_stock_location_id = fields.Many2one('stock.location', string='Source Location', )
    destination_stock_location_id = fields.Many2one('stock.location', string='Destination Location',
                                                    domain=[('usage', '=', 'transit')])
    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve'), ('transferring', 'Transferring'), ('done', 'Done'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')

    picking_count = fields.Integer(string='Transfers', compute='get_request_picking_count')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('transfer.request')
        return super(TransferRequest, self).create(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'done':
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

    @api.multi
    def get_request_picking_count(self):
        for rec in self:
            stock_picking_objects = self.env['stock.picking'].search(
                [('transfer_request_id', '=', rec.id)])
            rec.picking_count = len(stock_picking_objects)

    @api.multi
    def transfer_products(self):
        for rec in self:
            transfer_line_ids = [line.id for line in rec.transfer_request_line_ids if
                                 rec.transfer_request_line_ids and line.transfer_created == False]
            return {
                'name': _('Transfer Products'),
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'transfer.products.wizard',
                'view_id': self.env.ref('bi_transfer_request.transfer_products_wizard_form_view').id,
                'type': 'ir.actions.act_window',
                'context': {
                    'default_source_stock_location_id': rec.source_stock_location_id.id,
                    'default_destination_stock_location_id': rec.destination_stock_location_id.id,
                    'default_transfer_request_line_ids': transfer_line_ids,
                    'default_created_from': 'transfer_request',
                },
            }
