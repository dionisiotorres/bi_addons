# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class StockScrap(models.Model):
    _name = 'stock.scrap'
    _inherit = ['stock.scrap', 'mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = 'Scrap'

    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', related='product_id.uom_id', required=True,
                                     readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('done', 'Done')], string='Status', default="draft", track_visibility='onchange')

    reason = fields.Char(string='Reason', required=True)

    @api.multi
    def action_approve(self):
        for order in self:
            order.state = 'approved'
