from odoo import models, fields, api


class StockReport(models.TransientModel):
    _name = "wizard.stock.card"
    _description = "Stock Card Report"

    location = fields.Many2one('stock.location', string="Location", required=True)
    start_date = fields.Datetime(string="Start Date", required=True)
    end_date = fields.Datetime(string="End Date", required=True)

    @api.multi
    def export_xls(self):
        data = dict()
        data['location'] = self.location.id
        data['location_name'] = self.location.name
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        return {
            'data': data,
            'type': 'ir.actions.report',
            'report_name': 'bi_stock_card_report.report_stock_card_excel',
            'report_type': 'xlsx',
            'report_file': "Stock Card Report.xlsx",
        }
        # return self.env.ref('bi_stock_card_report.stock_card_xlsx').report_action(docids=self.id, data=data)
