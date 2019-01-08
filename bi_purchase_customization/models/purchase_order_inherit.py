# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    picking_partner_id = fields.Many2one('res.partner', string="Deliver To",
                                         related='picking_type_id.warehouse_id.partner_id')
