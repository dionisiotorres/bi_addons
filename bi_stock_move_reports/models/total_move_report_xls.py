# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import datetime
import pytz
from pytz import timezone
from datetime import timedelta


class TotalMoveReportXls(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.bi_stock_move_reports.total_move_report_xls'

    @api.model
    def generate_xlsx_report(self, workbook, data, wizard):

        if self._context and self._context.get('tz'):
            tz = timezone(self._context.get('tz'))
        else:
            tz = pytz.utc
        c_time = datetime.datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '+':
            date_time_from = datetime.datetime.strptime(str(wizard.date_from), DEFAULT_SERVER_DATETIME_FORMAT) + \
                        timedelta(hours=hour_tz, minutes=min_tz)
            date_time_to = datetime.datetime.strptime(str(wizard.date_to), DEFAULT_SERVER_DATETIME_FORMAT) + \
                             timedelta(hours=hour_tz, minutes=min_tz)
        else:
            date_time_from = datetime.datetime.strptime(str(wizard.date_from), DEFAULT_SERVER_DATETIME_FORMAT) - \
                        timedelta(hours=hour_tz, minutes=min_tz)
            date_time_to = datetime.datetime.strptime(str(wizard.date_to), DEFAULT_SERVER_DATETIME_FORMAT) - \
                             timedelta(hours=hour_tz, minutes=min_tz)


        worksheet = workbook.add_worksheet("Total Moves Report")
        row_no = 0
        col_no = 0

        f1 = workbook.add_format({'bold': True, 'font_color': 'black', })
        blue = workbook.add_format({'bold': True, 'font_color': 'blue', })
        gray = workbook.add_format({'bold': True, 'font_color': 'gray', })
        red = workbook.add_format({'bold': True, 'font_color': 'red', })
        green = workbook.add_format({'bold': True, 'font_color': 'green', })

        if wizard.type == 'all':
            worksheet.write(row_no, col_no, 'Total Moves Report', f1)
            row_no += 2
            worksheet.write(row_no, col_no, 'Date From: ', f1)
            worksheet.write(row_no, col_no + 1, datetime.datetime.strftime(date_time_from, DEFAULT_SERVER_DATETIME_FORMAT), )
            row_no += 1
            worksheet.write(row_no, col_no, 'Date To : ', f1)
            worksheet.write(row_no, col_no + 1, datetime.datetime.strftime(date_time_to, DEFAULT_SERVER_DATETIME_FORMAT), )
            row_no += 3

            # Header Of Table Data
            worksheet.write(row_no, col_no, "Date", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Reference", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Operation Type", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Type of Operation ", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Warehouse", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Product", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "From", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "To", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Item Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Opening Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Quantity Done", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Unit of Measure", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Item Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Ending Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "In/Out", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Total Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Transaction Type", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Status", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Initial Demand", f1)
            col_no += 1
            # End Of Header Table Data

            moves_domain = [('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('state', '=', 'done')]
            moves_objs = self.env['stock.move'].search(moves_domain)

            move_row = 8
            for move in moves_objs:
                move_row += 1
                move_date = datetime.datetime.strptime(str(move.date), DEFAULT_SERVER_DATETIME_FORMAT) + \
                        timedelta(hours=hour_tz, minutes=min_tz) if sign == '+' else datetime.datetime.strptime(str(move.date), DEFAULT_SERVER_DATETIME_FORMAT) - \
                        timedelta(hours=hour_tz, minutes=min_tz)
                worksheet.write(move_row, 0, datetime.datetime.strftime(move_date, DEFAULT_SERVER_DATETIME_FORMAT))
                worksheet.write(move_row, 1, move.reference)
                worksheet.write(move_row, 2, move.picking_type_id.name or ' ')
                worksheet.write(move_row, 3, move.picking_code or ' ')
                worksheet.write(move_row, 4, move.warehouse_id.name if move.warehouse_id else ' ')
                worksheet.write(move_row, 5, move.product_id.display_name or ' ')
                worksheet.write(move_row, 6, move.location_id.name or ' ')
                worksheet.write(move_row, 7, move.location_dest_id.name or ' ')
                worksheet.write(move_row, 8, str(move.item_standard_price))
                worksheet.write(move_row, 9, move.prod_opening_balance)
                worksheet.write(move_row, 10, str(move.quantity_done))
                worksheet.write(move_row, 11, move.product_uom.name)
                worksheet.write(move_row, 12, str(move.value))
                worksheet.write(move_row, 13, str(move.item_value))
                worksheet.write(move_row, 14, move.prod_ending_balance)
                worksheet.write(move_row, 15, move.xl_in_out_flag if (move.location_id.usage in ['transit'] or move.location_dest_id.usage in ['transit']) else move.in_out_flag)
                worksheet.write(move_row, 16, str(move.item_total_cost))
                worksheet.write(move_row, 17, move.transaction_type or ' ')
                worksheet.write(move_row, 18, move.state)
                worksheet.write(move_row, 19, str(move.product_uom_qty))
        elif wizard.type == 'per_location':
            moves_domain = [('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('state', '=', 'done'), '|', ('location_id', '=', wizard.location_id.id),
                            ('location_dest_id', '=', wizard.location_id.id)]
            moves_objs = self.env['stock.move'].search(moves_domain, order="date ASC")

            products_dict = {}
            for move in moves_objs:
                stock_balance = 0.0
                transit_balance = 0.0
                if move.in_out_flag == '1':
                    stock_balance += move.quantity_done
                elif move.in_out_flag == '-1':
                    stock_balance -= move.quantity_done
                if move.xl_in_out_flag == '1':
                    transit_balance += move.quantity_done
                    stock_balance += move.quantity_done
                elif move.xl_in_out_flag == '-1':
                    transit_balance -= move.quantity_done
                    stock_balance -= move.quantity_done
                stock_balance_value = move.value
                stock_balance_cost = move.item_total_cost
                transit_balance_cost = move.xl_item_total_cost
                total_balance_cost = stock_balance_cost + transit_balance_cost
                open_balance = move.prod_opening_balance
                end_balance = move.prod_ending_balance
                if move.product_id.id in products_dict:
                    products_dict[move.product_id.id][
                        'stock_qty_in'] += move.quantity_done if move.in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id][
                        'stock_qty_in_value'] += move.value if move.in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id][
                        'stock_qty_in_cost'] += move.item_total_cost if move.in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id][
                        'stock_qty_out'] += move.quantity_done if move.in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id][
                        'stock_qty_out_value'] += move.value if move.in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id][
                        'stock_qty_out_cost'] += move.item_total_cost if move.in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id]['stock_balance'] += stock_balance
                    products_dict[move.product_id.id]['stock_balance_value'] += stock_balance_value
                    products_dict[move.product_id.id]['stock_balance_cost'] += stock_balance_cost
                    products_dict[move.product_id.id][
                        'transit_in'] += move.quantity_done if move.xl_in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id][
                        'transit_out'] += move.quantity_done if move.xl_in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id]['transit_balance'] += transit_balance
                    products_dict[move.product_id.id]['transit_balance_cost'] += transit_balance_cost
                    products_dict[move.product_id.id]['total_balance_cost'] += total_balance_cost
                    if move.location_id.id in products_dict[move.product_id.id]['locations']:
                        products_dict[move.product_id.id]['locations'][move.location_id.id]['end_balance'] += end_balance
                    else:
                        products_dict[move.product_id.id]['locations'][move.location_id.id] = {'open_balance': open_balance, 'end_balance': end_balance}
                else:
                    products_dict[move.product_id.id] = {
                        'reference': move.product_id.default_code,
                        'product': move.product_id.display_name,
                        'cost': move.item_standard_price,
                        'stock_qty_in': move.quantity_done if move.in_out_flag == '1' else 0.0,
                        'stock_qty_in_value': move.value if move.in_out_flag == '1' else 0.0,
                        'stock_qty_in_cost': move.item_total_cost if move.in_out_flag == '1' else 0.0,
                        'stock_qty_out': move.quantity_done if move.in_out_flag == '-1' else 0.0,
                        'stock_qty_out_value': move.value if move.in_out_flag == '-1' else 0.0,
                        'stock_qty_out_cost': move.item_total_cost if move.in_out_flag == '-1' else 0.0,
                        'stock_balance': stock_balance,
                        'stock_balance_value': stock_balance_value,
                        'stock_balance_cost': stock_balance_cost,
                        'transit_in': move.quantity_done if move.xl_in_out_flag == '1' else 0.0,
                        'transit_out': move.quantity_done if move.xl_in_out_flag == '-1' else 0.0,
                        'transit_balance': transit_balance,
                        'transit_balance_cost': transit_balance_cost,
                        'total_balance_cost': total_balance_cost,
                        'locations': {
                            move.location_id.id: {'open_balance': open_balance, 'end_balance': end_balance}
                        },
                    }

            worksheet.write(row_no, col_no, 'Total Moves Per Location Report', f1)
            row_no += 2
            worksheet.write(row_no, col_no, 'Location: ', f1)
            worksheet.write(row_no, col_no + 1, wizard.location_id.display_name, )
            row_no += 2

            worksheet.write(row_no, col_no, 'Date From: ', f1)
            worksheet.write(row_no, col_no + 1, datetime.datetime.strftime(date_time_from, DEFAULT_SERVER_DATETIME_FORMAT), )
            row_no += 1
            worksheet.write(row_no, col_no, 'Date To : ', f1)
            worksheet.write(row_no, col_no + 1, datetime.datetime.strftime(date_time_to, DEFAULT_SERVER_DATETIME_FORMAT), )
            row_no += 3

            # Header Of Table Data
            worksheet.write(row_no, col_no, "Internal Reference", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Product", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Unit Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity In", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity In Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity In Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity Out", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity Out Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity Out Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Balance Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Balance Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Opening Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Ending Balance", f1)
            col_no += 1
            # End Of Header Table Data

            move_row = 8
            for line in products_dict.values():
                total_open_balance = 0.0
                total_end_balance = 0.0
                for loc in line['locations'].values():
                    total_open_balance += loc['open_balance']
                    total_end_balance += loc['end_balance']

                move_row += 1
                worksheet.write(move_row, 0, line['reference'])
                worksheet.write(move_row, 1, line['product'])
                worksheet.write(move_row, 2, line['cost'])
                worksheet.write(move_row, 3, line['stock_qty_in'])
                worksheet.write(move_row, 4, line['stock_qty_in_value'])
                worksheet.write(move_row, 5, line['stock_qty_in_cost'])
                worksheet.write(move_row, 6, line['stock_qty_out'])
                worksheet.write(move_row, 7, line['stock_qty_out_value'])
                worksheet.write(move_row, 8, line['stock_qty_out_cost'])
                worksheet.write(move_row, 9, line['stock_balance'])
                worksheet.write(move_row, 10, line['stock_balance_value'])
                worksheet.write(move_row, 11, line['stock_balance_cost'])
                worksheet.write(move_row, 12, total_open_balance)
                worksheet.write(move_row, 13, total_end_balance)
        elif wizard.type == 'per_warehouse':
            moves_domain = [('date', '>=', wizard.date_from), ('date', '<=', wizard.date_to), ('state', '=', 'done'), '|', '|', ('warehouse_id', '=', wizard.warehouse_id.id), ('location_id.display_name', 'ilike', wizard.warehouse_id.name),
                            ('location_dest_id.display_name', 'ilike', wizard.warehouse_id.name)]
            moves_objs = self.env['stock.move'].search(moves_domain, order="date ASC")

            products_dict = {}
            for move in moves_objs:
                stock_balance = 0.0
                transit_balance = 0.0
                if move.in_out_flag == '1':
                    stock_balance += move.quantity_done
                elif move.in_out_flag == '-1':
                    stock_balance -= move.quantity_done
                if move.xl_in_out_flag == '1':
                    transit_balance += move.quantity_done
                    stock_balance += move.quantity_done
                elif move.xl_in_out_flag == '-1':
                    transit_balance -= move.quantity_done
                    stock_balance -= move.quantity_done
                stock_balance_value = move.value
                stock_balance_cost = move.item_total_cost
                transit_balance_cost = move.xl_item_total_cost
                total_balance_cost = stock_balance_cost + transit_balance_cost
                open_balance = move.prod_opening_balance
                end_balance = move.prod_ending_balance
                warehouse = move.location_id.sudo().get_warehouse() or move.location_dest_id.sudo().get_warehouse()
                if move.product_id.id in products_dict:
                    products_dict[move.product_id.id]['stock_qty_in'] += move.quantity_done if move.in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id]['stock_qty_in_value'] += move.value if move.in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id]['stock_qty_in_cost'] += move.item_total_cost if move.in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id]['stock_qty_out'] += move.quantity_done if move.in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id]['stock_qty_out_value'] += move.value if move.in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id]['stock_qty_out_cost'] += move.item_total_cost if move.in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id]['stock_balance'] += stock_balance
                    products_dict[move.product_id.id]['stock_balance_value'] += stock_balance_value
                    products_dict[move.product_id.id]['stock_balance_cost'] += stock_balance_cost
                    products_dict[move.product_id.id]['transit_in'] += move.quantity_done if move.xl_in_out_flag == '1' else 0.0
                    products_dict[move.product_id.id]['transit_out'] += move.quantity_done if move.xl_in_out_flag == '-1' else 0.0
                    products_dict[move.product_id.id]['transit_balance'] += transit_balance
                    products_dict[move.product_id.id]['transit_balance_cost'] += transit_balance_cost
                    products_dict[move.product_id.id]['total_balance_cost'] += total_balance_cost

                    if warehouse and warehouse.id in products_dict[move.product_id.id]['warehouses']:
                        products_dict[move.product_id.id]['warehouses'][warehouse.id]['end_balance'] += end_balance
                    else:
                        products_dict[move.product_id.id]['warehouses'][warehouse.id] = {'open_balance': open_balance, 'end_balance': end_balance}
                else:
                    products_dict[move.product_id.id] = {
                        'reference': move.product_id.default_code,
                        'product': move.product_id.display_name,
                        'cost': move.item_standard_price,
                        'stock_qty_in': move.quantity_done if move.in_out_flag == '1' else 0.0,
                        'stock_qty_in_value': move.value if move.in_out_flag == '1' else 0.0,
                        'stock_qty_in_cost': move.item_total_cost if move.in_out_flag == '1' else 0.0,
                        'stock_qty_out': move.quantity_done if move.in_out_flag == '-1' else 0.0,
                        'stock_qty_out_value': move.value if move.in_out_flag == '-1' else 0.0,
                        'stock_qty_out_cost': move.item_total_cost if move.in_out_flag == '-1' else 0.0,
                        'stock_balance': stock_balance,
                        'stock_balance_value': stock_balance_value,
                        'stock_balance_cost': stock_balance_cost,
                        'transit_in': move.quantity_done if move.xl_in_out_flag == '1' else 0.0,
                        'transit_out': move.quantity_done if move.xl_in_out_flag == '-1' else 0.0,
                        'transit_balance': transit_balance,
                        'transit_balance_cost': transit_balance_cost,
                        'total_balance_cost': total_balance_cost,
                        'warehouses': {}
                    }
                    if warehouse:
                        products_dict[move.product_id.id]['warehouses'][warehouse.id] = {'open_balance': open_balance, 'end_balance': end_balance}

            worksheet.write(row_no, col_no, 'Total Moves Per Warehouse Report', f1)
            row_no += 2
            worksheet.write(row_no, col_no, 'Warehouse: ', f1)
            worksheet.write(row_no, col_no + 1, wizard.warehouse_id.name, )
            row_no += 2

            worksheet.write(row_no, col_no, 'Date From: ', f1)
            worksheet.write(row_no, col_no + 1, datetime.datetime.strftime(date_time_from, DEFAULT_SERVER_DATETIME_FORMAT), )
            row_no += 1
            worksheet.write(row_no, col_no, 'Date To : ', f1)
            worksheet.write(row_no, col_no + 1, datetime.datetime.strftime(date_time_to, DEFAULT_SERVER_DATETIME_FORMAT), )
            row_no += 3

            # Header Of Table Data
            worksheet.write(row_no, col_no, "Internal Reference", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Product", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Unit Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity In", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity In Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity In Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity Out", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity Out Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Quantity Out Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Balance Value", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Stock Balance Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Transit In", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Transit Out", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Transit Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Transit Balance Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Total Balance Cost", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Opening Balance", f1)
            col_no += 1
            worksheet.write(row_no, col_no, "Ending Balance", f1)
            col_no += 1
            # End Of Header Table Data

            move_row = 8
            for line in products_dict.values():
                total_open_balance = 0.0
                total_end_balance = 0.0
                for wh in line['warehouses'].values():
                    total_open_balance += wh['open_balance']
                    total_end_balance += wh['end_balance']

                move_row += 1
                worksheet.write(move_row, 0, line['reference'])
                worksheet.write(move_row, 1, line['product'])
                worksheet.write(move_row, 2, line['cost'])
                worksheet.write(move_row, 3, line['stock_qty_in'])
                worksheet.write(move_row, 4, line['stock_qty_in_value'])
                worksheet.write(move_row, 5, line['stock_qty_in_cost'])
                worksheet.write(move_row, 6, line['stock_qty_out'])
                worksheet.write(move_row, 7, line['stock_qty_out_value'])
                worksheet.write(move_row, 8, line['stock_qty_out_cost'])
                worksheet.write(move_row, 9, line['stock_balance'])
                worksheet.write(move_row, 10, line['stock_balance_value'])
                worksheet.write(move_row, 11, line['stock_balance_cost'])
                worksheet.write(move_row, 12, line['transit_in'])
                worksheet.write(move_row, 13, line['transit_out'])
                worksheet.write(move_row, 14, line['transit_balance'])
                worksheet.write(move_row, 15, line['transit_balance_cost'])
                worksheet.write(move_row, 16, line['total_balance_cost'])
                worksheet.write(move_row, 17, total_open_balance)
                worksheet.write(move_row, 18, total_end_balance)