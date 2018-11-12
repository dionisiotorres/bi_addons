# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TransferProductsWizard(models.TransientModel):
    _name = 'transfer.products.wizard'

    def get_transfer_request_products(self):
        transfer_request_id = self.env.context.get('active_id')
        created_from_value = self._context.get('default_created_from')
        transfer_request = self.env['transfer.request'].browse(transfer_request_id)
        transfer_line_ids = [line.id for line in transfer_request.transfer_request_line_ids if
                             transfer_request.transfer_request_line_ids and created_from_value == 'transfer_request']
        return [('id', 'in', transfer_line_ids)]

    transfer_request_line_ids = fields.Many2many('transfer.request.line', string='Transferred Products',
                                                 domain=get_transfer_request_products, required=1)
    source_stock_location_id = fields.Many2one('stock.location', string='Source Location', required=1)
    destination_stock_location_id = fields.Many2one('stock.location', string='Destination Location',
                                                    domain=[('usage', '=', 'transit')], required=1)
    created_from = fields.Selection(
        [('transfer_request', 'Transfer Request'), (('transfer_request_line', 'Transfer Request Line'))],
        string='Created From')

    @api.multi
    def create_transfer_for_products(self):
        for wizard in self:
            print("hereeeeee")
