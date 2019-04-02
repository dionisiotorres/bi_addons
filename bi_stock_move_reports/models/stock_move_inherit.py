# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    in_out_flag = fields.Selection([
        ('1', '1'),
        ('0', '0'),
        ('-1', '-1')
    ], string='In/Out', compute='_compute_in_out_flag', store=1, copy=False)
    xl_in_out_flag = fields.Selection([
        ('1', '1'),
        ('0', '0'),
        ('-1', '-1')
    ], string='In/Out', compute='_compute_xl_in_out_flag', store=1, copy=False)
    item_standard_price = fields.Float('Item Cost', related='product_id.standard_price', company_dependent=True, digits=dp.get_precision('Product Price'),
        groups="base.group_user")
    item_total_cost = fields.Float('Total Cost', compute='_compute_total_cost', copy=False)
    xl_item_total_cost = fields.Float('xl Total Cost', compute='_compute_total_cost', copy=False)
    item_value = fields.Float('Item Value', compute='_compute_item_value', copy=False)
    transaction_type = fields.Selection([
        ('receipt', 'Receipt'),
        ('delivery', 'Delivery'),
        ('manufacturing', 'Manufacturing'),
        ('internal_transfer', 'Internal Transfer'),
        ('scrap', 'Scrap'),
        ('inventory_adjustment', 'Inventory Adjustment'),
    ], string='Transaction Type', compute='_compute_transaction_type', store=1, copy=False)
    prod_opening_balance = fields.Float('Opening Balance', compute='_compute_balance')
    prod_ending_balance = fields.Float('Ending Balance', compute='_compute_balance')

    @api.multi
    @api.depends('quantity_done', 'date', 'location_id', 'product_id', 'in_out_flag')
    def _compute_balance(self):
        move_obj = self.env['stock.move']
        for rec in self:
            opening = 0.0
            if rec.date and rec.location_id and rec.product_id:
                objs = move_obj.search([('product_id', '=', rec.product_id.id), ('location_id', '=', rec.location_id.id), ('date', '<', rec.date)])
                for mv in objs:
                    opening += mv.quantity_done
            rec.prod_opening_balance = opening
            rec.prod_ending_balance = opening + (rec.quantity_done * int(rec.in_out_flag))


    @api.multi
    @api.depends('location_id', 'location_id.usage', 'location_id.scrap_location', 'location_dest_id', 'location_dest_id.usage', 'location_dest_id.scrap_location')
    def _compute_transaction_type(self):
        for rec in self:
            if rec.location_id.scrap_location or rec.location_dest_id.scrap_location:
                rec.transaction_type = 'scrap'
            else:
                if rec.location_id.usage in ['supplier']:
                    rec.transaction_type = 'receipt'
                elif rec.location_dest_id.usage in ['customer']:
                    rec.transaction_type = 'delivery'
                elif rec.location_id.usage in ['production'] or rec.location_dest_id.usage in ['production']:
                    rec.transaction_type = 'manufacturing'
                elif rec.location_id.usage in ['inventory'] or rec.location_dest_id.usage in ['inventory']:
                    rec.transaction_type = 'inventory_adjustment'

    @api.multi
    @api.depends('location_id', 'location_id.usage', 'location_dest_id', 'location_dest_id.usage')
    def _compute_in_out_flag(self):
        for rec in self:
            rec.in_out_flag = '0'
            if rec.location_id.usage in ['supplier', 'customer', 'production', 'inventory']:
                rec.in_out_flag = '1'
            if rec.location_dest_id.usage in ['supplier', 'customer', 'production', 'inventory']:
                rec.in_out_flag = '-1'
            if rec.location_id.usage in ['transit'] or rec.location_dest_id.usage in ['transit']:
                rec.in_out_flag = '0'

    @api.multi
    @api.depends('location_id', 'location_id.usage', 'location_dest_id', 'location_dest_id.usage')
    def _compute_xl_in_out_flag(self):
        for rec in self:
            rec.xl_in_out_flag = '0'
            if rec.location_id.usage in ['transit']:
                rec.xl_in_out_flag = '-1'
            if rec.location_dest_id.usage in ['transit']:
                rec.xl_in_out_flag = '1'

    @api.multi
    @api.depends('value', 'quantity_done')
    def _compute_item_value(self):
        for rec in self:
            if rec.quantity_done:
                rec.item_value = rec.value / rec.quantity_done

    @api.multi
    @api.depends('item_standard_price', 'xl_in_out_flag', 'in_out_flag', 'quantity_done')
    def _compute_total_cost(self):
        for rec in self:
            rec.item_total_cost = rec.item_standard_price * rec.quantity_done * int(rec.in_out_flag)
            if rec.xl_in_out_flag in ['1', '-1']:
                rec.xl_item_total_cost = rec.item_standard_price * rec.quantity_done * int(rec.xl_in_out_flag)
            else:
                rec.xl_item_total_cost = 0.0