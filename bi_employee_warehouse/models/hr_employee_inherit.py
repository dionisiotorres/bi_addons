# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo import exceptions
from odoo.exceptions import ValidationError
from datetime import datetime


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    dest_location_id = fields.Many2one('stock.location', string='Destination Location')
    operation_type_id = fields.Many2one('stock.picking.type', string='Operation Type')


    @api.onchange('user_id', 'warehouse_id')
    def onchange_warehouse(self):
        if self.warehouse_id:
            locations = self.env['stock.location'].search([('usage', '=', 'transit')])

            dest_location_id = False
            for loc in locations:
                if self.warehouse_id.id == loc.get_warehouse().id:
                    dest_location_id = loc.id
                    break
            self.dest_location_id = dest_location_id

            type_obj = self.env['stock.picking.type']
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', self.warehouse_id.id)], limit=1)
            if not types:
                types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)], limit=1)

            if types:
                self.operation_type_id = types[0].id
            else:
                self.operation_type_id = False

    @api.model
    def get_warehouse_operations(self, warehouse_id):
        dest_location_id = False
        operation_type_id = False
        if warehouse_id:
            warehouse = self.env['stock.warehouse'].browse([warehouse_id])
            locations = self.env['stock.location'].search([('usage', '=', 'transit')])
            for loc in locations:
                if warehouse.id == loc.get_warehouse().id:
                    dest_location_id = loc.id

            type_obj = self.env['stock.picking.type']
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', warehouse.id)], limit=1)
            if not types:
                types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)], limit=1)
            if types:
                operation_type_id = types[0].id
        return dest_location_id, operation_type_id

    @api.model
    def create(self, vals):
        if vals.get('warehouse_id'):
            dest_location_id, operation_type_id = self.get_warehouse_operations(vals.get('warehouse_id'))
            vals.update({
                'dest_location_id': dest_location_id,
                'operation_type_id': operation_type_id,
            })
        res = super(HrEmployeeInherit, self).create(vals)
        if res.user_id:
            res.user_id.write({
                'warehouse_id': res.warehouse_id.id,
                'dest_location_id': res.dest_location_id.id,
                'operation_type_id': res.operation_type_id.id,
            })
        return res

    @api.multi
    def write(self, vals):
        if vals.get('warehouse_id') or 'warehouse_id' in vals:
            dest_location_id, operation_type_id = self.get_warehouse_operations(vals.get('warehouse_id'))
            vals.update({
                'dest_location_id': dest_location_id,
                'operation_type_id': operation_type_id,
            })
        res = super(HrEmployeeInherit, self).write(vals)
        for emp in self:
            if emp.user_id:
                emp.user_id.write({
                    'warehouse_id': emp.warehouse_id.id,
                    'dest_location_id': emp.dest_location_id.id,
                    'operation_type_id': emp.operation_type_id.id,
                })
        return res


