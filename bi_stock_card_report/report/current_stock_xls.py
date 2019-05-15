from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import models, _


class StandardReportXlsx(models.AbstractModel):
    _name = 'report.bi_stock_card_report.report_stock_card_excel'
    _inherit = 'report.report_xlsx.abstract'

    def get_lines(self, data):
        self.env.cr.execute(
            """WITH
                source as (select t1.product_id, sum(t1.product_uom_qty) as openin from stock_move as t1
                where (t1.location_id = %s )
                and t1.date < %s
                and t1.state = 'done'
                group by t1.product_id ),

                dist as (select t1.product_id, sum(t1.product_uom_qty) as openout from stock_move as t1
                where (t1.location_dest_id =%s )
                and t1.date < %s
                and t1.state = 'done'
                group by t1.product_id),

                qtyin as (select t1.product_id, sum(t1.product_uom_qty) as qtyin from stock_move as t1
                where (t1.location_id = %s )
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                group by t1.product_id ),

                qtyout as (select t1.product_id, sum(t1.product_uom_qty) as qtyout from stock_move as t1
                where (t1.location_dest_id = %s)
                and t1.date BETWEEN %s AND %s
                and t1.state = 'done'
                group by t1.product_id)

                select product_template.name, dist.openout,
                source.openin,
                (coalesce(dist.openout,0)- coalesce(source.openin,0)) as openBlance
                ,qtyin.qtyin,qtyout.qtyout,
                (coalesce(dist.openout,0)- coalesce(source.openin,0)) +coalesce(qtyin.qtyin,0) - +coalesce(qtyout.qtyout,0) as endblance
                from dist full join source on dist.product_id = source.product_id
                full join qtyin on qtyin.product_id = source.product_id
                full join qtyout on qtyout.product_id = source.product_id
                left join product_product on product_product.id = GREATEST(dist.product_id,source.product_id,qtyin.product_id,qtyout.product_id)
                left join product_template on product_template.id= product_product.product_tmpl_id
                order by product_template.name""",(
                data['location'], data['start_date'], data['location'], data['start_date'],
                data['location'],
                data['start_date'], data['end_date'], data['location'], data['start_date'],
                data['end_date']))
        lines = self.env.cr.fetchall()
        return lines

    def generate_xlsx_report(self, workbook, data, objs):
        lines = self.get_lines(data)
        sheet = workbook.add_worksheet('Stock Info')
        format1 = workbook.add_format(
            {'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter',
             'bold': True})
        format11 = workbook.add_format(
            {'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format21 = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format21_unbolded = workbook.add_format(
            {'font_size': 10, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True,
             'bold': False})
        format_left_align_left = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'right': False, 'left': True, 'bottom': True, 'top': True,
             'bold': True})
        format_left_align_right = workbook.add_format(
            {'font_size': 10, 'align': 'left', 'right': True, 'left': False, 'bottom': True, 'top': True,
             'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
        red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8,
                                        'bg_color': 'red'})
        justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12})
        format3.set_align('center')
        font_size_8.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range('A1:D3', 'Report Date: ' + str(datetime.now().strftime("%Y-%m-%d %H:%M %p")), format1)
        sheet.write(0, 4, 'From: ', format_left_align_left)
        sheet.merge_range('F1:H1', data['start_date'], format_left_align_right)
        sheet.write(1, 4, 'To: ', format_left_align_left)
        sheet.merge_range('F2:H2', data['end_date'], format_left_align_right)
        sheet.write(2, 4, 'Location: ', format_left_align_left)
        sheet.merge_range('F3:H3', data['location_name'], format_left_align_right)

        sheet.set_column(0, 0, 40)
        sheet.set_column(1, 1, 15)
        sheet.set_column(2, 2, 10)
        sheet.set_column(3, 3, 12)
        sheet.set_column(4, 4, 15)

        sheet.write(3, 0, "Name", format21)
        sheet.write(3, 1, "Open Balance", format21)
        sheet.write(3, 2, "Qty In", format21)
        sheet.write(3, 3, "Qty Out", format21)
        sheet.write(3, 4, "End Balance", format21)

        count = 4
        for line in lines:
            sheet.write(count, 0, line[0], format21_unbolded)
            sheet.write(count, 1, line[3], format21_unbolded)
            sheet.write(count, 2, line[4], format21_unbolded)
            sheet.write(count, 3, line[5], format21_unbolded)
            sheet.write(count, 4, line[6], format21_unbolded)
            count += 1
