# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockMoveInherit(models.Model):
    _inherit = 'stock.move.line'

    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', index=True)
    vendor = fields.Many2one('res.partner', string="Vendor", related='picking_id.partner_id')