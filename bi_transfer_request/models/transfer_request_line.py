# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TransferRequestLine(models.Model):
    _name = 'transfer.request.line'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    transfer_request_id = fields.Many2one('transfer.request', string='Transfer Request')
    transferred_qty = fields.Float(string='Transferred Qty', )
    transfer_created = fields.Boolean(string='Transfer Created')
    qty = fields.Float(string='Qty', required=True, default=1.0)
    notes = fields.Char(string='Notes')
    product_uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id',
                                     store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('approve', 'Approve'), ('transferring', 'Transferring'), ('done', 'Done'),
         ('cancelled', 'Cancelled')], string='State', default='draft', related='transfer_request_id.state')

    @api.constrains('transferred_qty')
    def check_transferred_qty(self):
        for line in self:
            if line.transferred_qty and line.qty:
                if line.transferred_qty > line.qty:
                    raise ValidationError(_('Transferred qty must be less than or equal ordered qty.'))

    @api.onchange('product_id')
    def get_uom_from_product(self):
        for line in self:
            if line.product_id:
                line.product_uom_id = line.product_id.uom_id.id

    @api.multi
    def create_line_transfer(self):
        for line in self:
            return {
                'name': _('Transfer Product'),
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'transfer.products.wizard',
                'view_id': self.env.ref('bi_transfer_request.transfer_products_wizard_form_view').id,
                'type': 'ir.actions.act_window',
                'context': {
                    'default_transfer_request_id': line.transfer_request_id.id,
                    'default_source_stock_location_id': line.transfer_request_id.source_stock_location_id.id,
                    'default_destination_stock_location_id': line.transfer_request_id.destination_stock_location_id.id,
                    'default_transfer_request_line_ids': [line.id if line.transfer_created == False else False],
                    'default_created_from': 'transfer_request_line',
                },
            }

    @api.model
    def create(self, vals):
        # check transfer request state
        if 'transfer_request_id' in vals and vals['transfer_request_id']:
            req = self.env['transfer.request'].browse([vals['transfer_request_id']])
            if req.state not in ['draft']:
                raise ValidationError(_('You can add transfer request line in draft state only.'))
        res = super(TransferRequestLine, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.transfer_request_id and rec.transfer_request_id.state not in ['draft']:
                raise ValidationError(_('You can delete transfer request line in draft state only.'))
        return super(TransferRequestLine, self).unlink()