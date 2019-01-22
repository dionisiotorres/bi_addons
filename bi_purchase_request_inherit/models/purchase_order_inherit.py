# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    note = fields.Char(string='Note')

