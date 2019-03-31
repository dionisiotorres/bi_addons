# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StockMoveReportWizardReport(models.TransientModel):
    _name = 'stock.move.report.wizard'

    date_from = fields.Datetime(string='Date From')
    date_to = fields.Datetime(string='Date To')
    type = fields.Selection([
        ('all', 'All'),
        ('per_location', 'Per Location'),
        ('per_warehouse', 'Per Warehouse')
    ], string='Type', required=1)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    location_id = fields.Many2one('stock.location', 'Location')


    @api.constrains('date_from', 'date_to')
    def _constrain_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError(_('Date From Must Be Greater Than Date To!'))

    @api.multi
    def view_report(self):
        data = self.read()[0]
        datas = {
            'ids': [],
            'model': 'stock.move',
            'form': data
        }
        return self.env['ir.actions.report'].search(
            [('report_name', '=', 'bi_stock_move_reports.total_move_report_xls'),
             ('report_type', '=', 'xlsx')],
            limit=1).report_action(self, data=datas)
