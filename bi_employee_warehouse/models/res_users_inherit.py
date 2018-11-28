# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError
from datetime import datetime


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    dest_location_id = fields.Many2one('stock.location', string='Destination Location')
    operation_type_id = fields.Many2one('stock.picking.type', string='Operation Type')