# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TransferProductsWizard(models.TransientModel):
    _name = 'transfer.products.wizard'

    def get_transfer_request_products(self):
        transfer_request_id = self.env.context.get('active_id')
        created_from_value = self._context.get('default_created_from')
        transfer_request = self.env['transfer.request'].browse(transfer_request_id)
        if created_from_value == 'transfer_request':
            transfer_line_ids = [line.id for line in transfer_request.transfer_request_line_ids if
                                 transfer_request.transfer_request_line_ids]
        else:
            transfer_line_ids = self._context.get('default_transfer_request_line_ids')
        return [('id', 'in', transfer_line_ids)]

    transfer_request_line_ids = fields.Many2many('transfer.request.line', string='Transferred Products',
                                                 domain=get_transfer_request_products)
    source_stock_location_id = fields.Many2one('stock.location', string='Source Location', required=1)
    destination_stock_location_id = fields.Many2one('stock.location', string='Destination Location',
                                                    domain=[('usage', '=', 'transit')], required=1)
    created_from = fields.Selection(
        [('transfer_request', 'Transfer Request'), ('transfer_request_line', 'Transfer Request Line')],
        string='Created From')

    @api.multi
    def create_transfer_for_products(self):
        for wizard in self:
            picking_line_vals = []
            transfer_request = False
            internal_picking_type_id = self.env['stock.picking.type'].search(
                [('code', '=', 'internal')], limit=1).id
            if not internal_picking_type_id:
                raise ValidationError(_('Please configure internal transfer.'))

            for line in wizard.transfer_request_line_ids:
                picking_line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'name': line.product_id.name,
                    'product_uom_qty': line.transferred_qty,
                    'product_uom': line.product_uom_id.id,
                    'company_id': self.env.user.company_id.id,
                    'location_id': wizard.source_stock_location_id.id,
                    'location_dest_id': wizard.destination_stock_location_id.id,
                }))
            if self._context.get('default_created_from') == 'transfer_request':
                transfer_request_id = self.env.context.get('active_id')
                transfer_request = self.env['transfer.request'].browse(transfer_request_id)
            else:

                transfer_request_id = self._context.get('default_transfer_request_id')
                transfer_request = self.env['transfer.request'].browse(transfer_request_id)
            picking_vals = {
                'origin': transfer_request.name,
                'scheduled_date': fields.Datetime.now(),
                'picking_type_id': internal_picking_type_id,
                'location_id': wizard.source_stock_location_id.id,
                'location_dest_id': wizard.destination_stock_location_id.id,
                'company_id': self.env.user.company_id.id,
                'move_type': 'direct',
                'state': 'draft',
                'move_lines': picking_line_vals,
                'transfer_request_id': transfer_request.id

            }
            created_picking = self.env['stock.picking'].create(picking_vals)
            if created_picking:
                for line in wizard.transfer_request_line_ids:
                    line.transfer_created = True
