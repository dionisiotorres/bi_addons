# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockScrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['stock.scrap', 'mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = 'Scrap'

    @api.model
    def get_location_domain(self):
        internal_location_objects = self.env['stock.location'].search([('usage', '=', 'internal')])
        if self.env.user.warehouse_id:
            return [('id', '=', self.env.user.warehouse_id.lot_stock_id.id)]
        else:
            return [('id', 'in', internal_location_objects.ids)]

    def get_default_user_location_id(self):
        warehouse = self.env.user.warehouse_id
        if warehouse:
            return warehouse.lot_stock_id.id
        else:
            return None

    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', related='product_id.uom_id', required=True,
                                     readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done')], string='Status', default="draft", track_visibility='onchange')

    reason = fields.Char(string='Reason', required=True)
    location_id = fields.Many2one(
        'stock.location', 'Location', domain=get_location_domain, default=get_default_user_location_id,
        required=True, states={'done': [('readonly', True)]}, )

    @api.multi
    def action_approve(self):
        for order in self:
            order.state = 'approved'
