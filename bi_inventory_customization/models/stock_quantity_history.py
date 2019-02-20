# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StockQuantityHistoryInherit(models.TransientModel):
    _inherit = 'stock.quantity.history'

    filter_by = fields.Selection([('location','Location'), ('warehouse','Warehouse')], string='Filter By')
    location_id = fields.Many2one('stock.location', 'Location', domain="[('usage', 'in', ['internal','transit'])]")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')

    def open_table(self):
        self.ensure_one()
        location = False
        warehouse = False
        compute_report = False
        if self.compute_at_date and self.filter_by == 'location' and self.location_id:
            location = self.location_id.id
            compute_report = True

        if self.compute_at_date and self.filter_by == 'warehouse' and self.warehouse_id:
            warehouse = self.warehouse_id.id
            compute_report = True

        return super(StockQuantityHistoryInherit,self.with_context(location=location, warehouse=warehouse, compute_report=compute_report)).open_table()

    @api.onchange('compute_at_date','filter_by')
    def onchange_compute_at_date(self):
        for rec in self:
            if not rec.compute_at_date:
                rec.filter_by = False
                rec.location_id = False
                rec.warehouse_id = False
            if rec.compute_at_date and rec.filter_by == 'location':
                rec.warehouse_id = False
            if rec.compute_at_date and rec.filter_by == 'warehouse':
                rec.location_id = False