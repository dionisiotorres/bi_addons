# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer_request_id = fields.Many2one('transfer.request', string='Transfer Request')


class TransferRequestReason(models.Model):
    _name = 'transfer.request.reason'

    name = fields.Char(string='Transfer Reason')


class TransferRequest(models.Model):
    _name = 'transfer.request'
    _inherit = ['mail.thread', 'resource.mixin']

    # old implementation
    # def _get_default_requester(self):
    #     emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
    #     if emp:
    #         return emp[0].id
    #     else:
    #         return False

    @api.model
    def _get_default_requested_by(self):
        return self.env['res.users'].browse(self.env.uid)

    @api.model
    def _default_dest_location(self):
        if self.env.user.dest_location_id:
            return self.env.user.dest_location_id.id
        else:
            return False

    name = fields.Char(string='Name', readonly=1)
    requested_by = fields.Many2one('res.users', 'Requested by', required=True, default=_get_default_requested_by)
    # requested_by_employee_id = fields.Many2one('hr.employee', string='Requester', default=_get_default_requester)
    # requested_for_employee_id = fields.Many2one('hr.employee', string='Requested For')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', )
    cancel_reason = fields.Html(string='Cancellation Reason')
    transfer_request_line_ids = fields.One2many('transfer.request.line', 'transfer_request_id',
                                                string='Transferred Products')
    source_stock_location_id = fields.Many2one('stock.location', string='Source Location', domain=[('usage', '=', 'internal')])
    destination_stock_location_id = fields.Many2one('stock.location', string='Destination Location',
                                                    domain=[('usage', '=', 'transit')], default=_default_dest_location)
    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve'), ('transferring', 'Transferring'), ('done', 'Done'),
         ('cancelled', 'Cancelled')], string='State', default='draft', track_visibility='onchange')

    picking_count = fields.Integer(string='Transfers', compute='get_request_picking_count')
    transfer_reason = fields.Many2one('transfer.request.reason', string='Transfer Reason')

    @api.model
    def create(self, vals):
        if not self.env.user.dest_location_id:
            raise ValidationError(_('Please configure destination location in current user related employee.'))
        vals['name'] = self.env['ir.sequence'].next_by_code('transfer.request')
        vals.update({
            'requested_by': self.env.uid,
            'destination_stock_location_id': self.env.user.dest_location_id.id,
        })
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
            if not rec.cancel_reason or rec.cancel_reason == '<p><br></p>':
                raise ValidationError(_('Please add reason for canceling request first.'))
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
            rec.create_transfer_for_products()
            rec.set_state_to_transferring()

            # old implementation
            # transfer_line_ids = [line.id for line in rec.transfer_request_line_ids if
            #                      rec.transfer_request_line_ids and line.transfer_created == False]
            # return {
            #     'name': _('Transfer Products'),
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'target': 'new',
            #     'res_model': 'transfer.products.wizard',
            #     'view_id': self.env.ref('bi_transfer_request.transfer_products_wizard_form_view').id,
            #     'type': 'ir.actions.act_window',
            #     'context': {
            #         'default_source_stock_location_id': rec.source_stock_location_id.id,
            #         'default_destination_stock_location_id': rec.destination_stock_location_id.id,
            #         'default_transfer_request_line_ids': transfer_line_ids,
            #         'default_created_from': 'transfer_request',
            #     },
            # }


    def create_transfer_for_products(self):
        picking_line_vals = []
        source_warehouse = self.source_stock_location_id.get_warehouse()
        internal_picking_type = self.env['stock.picking.type'].sudo().search(
            [('code', '=', 'internal'), ('warehouse_id', '=', source_warehouse.id)], limit=1)
        if not internal_picking_type:
            raise ValidationError(_('Please configure internal transfer.'))
        else:
            internal_picking_type_id = internal_picking_type.id

        for line in self.transfer_request_line_ids:
            if line.transfer_created == False:
                picking_line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.transferred_qty or line.qty,
                    'product_uom': line.product_uom_id.id,
                    'company_id': self.env.user.company_id.id,
                    'location_id': self.source_stock_location_id.id,
                    'location_dest_id': self.destination_stock_location_id.id,
                }))
        if len(picking_line_vals):
            picking_vals = {
                'origin': self.name,
                'scheduled_date': fields.Datetime.now(),
                'picking_type_id': internal_picking_type_id,
                'location_id': self.source_stock_location_id.id,
                'location_dest_id': self.destination_stock_location_id.id,
                'company_id': self.env.user.company_id.id,
                'move_type': 'direct',
                'state': 'draft',
                'move_lines': picking_line_vals,
                'transfer_request_id': self.id

            }
            created_picking = self.env['stock.picking'].sudo().create(picking_vals)
            if created_picking:
                created_picking.action_confirm()
                for line in self.transfer_request_line_ids:
                    line.transfer_created = True