# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ItemCardWizard(models.TransientModel):
    """Item Card"""

    _name = "item.card.wizard"
    _description = "Item Card Wizard"

    date_from = fields.Datetime(string='Date From', required=True)
    date_to = fields.Datetime(string='Date To', default=fields.Datetime.now(), required=True)
    product_id = fields.Many2one('product.product', string='Product')
    report_view = fields.Selection([('detailed', 'Detailed'), ('total', 'Total')],
                                   default='detailed', string='Report View', required=True,
                                   help='Choose how you want to view the report(detailed for viewing transactions - total for viewing without transactions)')
    show_cost = fields.Boolean(string='Show Cost', help='Show Cost Columns')
    group_by_type = fields.Selection([('warehouse', 'Warehouse'), ('location', 'Location')], string='Group By')

    filter_by = fields.Selection([('warehouse', 'Warehouse'), ('location', 'Location')], string='Filter By',
                                 help='Filter by warehouse or location')

    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    location_ids = fields.Many2many('stock.location', string='Locations')

    @api.constrains('date_from', 'date_to')
    def _constrain_dates(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise UserError(_('Date From Must Be Greater Than Date To!'))

    @api.multi
    def view_report(self):
        self.ensure_one()
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('state', '=', 'done')]
        if self.product_id:
            domain += [('product_id', '=', self.product_id.id)]

        warehouse_locations = []
        if self.filter_by and self.filter_by == 'warehouse' and self.warehouse_ids:
            for warehouse in self.warehouse_ids:
                location_ids = self.env['stock.location'].search([('id', 'child_of', warehouse.view_location_id.id)])

                warehouse_locations += location_ids.ids
            domain += ['|', ('location_id', 'in', warehouse_locations), ('location_dest_id', 'in', warehouse_locations)]

        if self.filter_by and self.filter_by == 'location' and self.location_ids:
            domain += ['|', ('location_id', 'in', self.location_ids.ids),
                       ('location_dest_id', 'in', self.location_ids.ids)]
        without_cost_tree_view_id = self.env.ref('bi_item_card_report.view_item_card_without_cost_tree').id
        without_cost_location_tree_view_id = self.env.ref('bi_item_card_report.view_item_card_without_cost_loc_tree').id
        without_cost_warehouse_tree_view_id = self.env.ref('bi_item_card_report.view_item_card_without_cost_wh_tree').id

        cost_tree_view_id = self.env.ref('bi_item_card_report.view_item_card_with_cost_tree').id
        cost_location_tree_view_id = self.env.ref('bi_item_card_report.view_item_card_with_cost_loc_tree').id
        cost_warehouse_tree_view_id = self.env.ref('bi_item_card_report.view_item_card_with_cost_wh_tree').id

        without_cost_pivot_view_id = self.env.ref('bi_item_card_report.view_item_card_without_cost_pivot').id
        without_cost_location_pivot_view_id = self.env.ref(
            'bi_item_card_report.view_item_card_without_cost_loc_pivot').id
        without_cost_warehouse_pivot_view_id = self.env.ref(
            'bi_item_card_report.view_item_card_without_cost_wh_pivot').id

        cost_pivot_view_id = self.env.ref('bi_item_card_report.view_item_card_with_cost_pivot').id
        cost_location_pivot_view_id = self.env.ref('bi_item_card_report.view_item_card_with_cost_loc_pivot').id
        cost_warehouse_pivot_view_id = self.env.ref('bi_item_card_report.view_item_card_with_cost_wh_pivot').id

        if self.show_cost:
            if self.group_by_type:
                if self.group_by_type == 'location':
                    tree_view_id = cost_location_tree_view_id
                    pivot_view_id = cost_location_pivot_view_id
                else:
                    tree_view_id = cost_warehouse_tree_view_id
                    pivot_view_id = cost_warehouse_pivot_view_id

            else:
                tree_view_id = cost_tree_view_id
                pivot_view_id = cost_pivot_view_id
        else:
            if self.group_by_type:
                if self.group_by_type == 'location':
                    tree_view_id = without_cost_location_tree_view_id
                    pivot_view_id = without_cost_location_pivot_view_id
                else:
                    tree_view_id = without_cost_warehouse_tree_view_id
                    pivot_view_id = without_cost_warehouse_pivot_view_id

            else:
                tree_view_id = without_cost_tree_view_id
                pivot_view_id = without_cost_pivot_view_id
        default_product_group = False
        default_location_group = False
        default_warehouse_group = False

        if self.report_view == 'total':
            default_product_group = True
        if self.group_by_type and self.group_by_type == 'location':
            default_location_group = True
        if self.group_by_type and self.group_by_type == 'warehouse':
            default_warehouse_group = True

        # We pass `to_date` in the context so that `qty_available` will be computed across
        # moves until date.
        action = {
            'type': 'ir.actions.act_window',
            'views': [(tree_view_id, 'tree'), (pivot_view_id, 'pivot')],
            'view_mode': 'tree,pivot',
            'name': _('Item Card'),
            'res_model': 'stock.move.line',
            'domain': domain,
            'context': dict(self.env.context, date_from=self.date_from, date_to=self.date_to,
                            product_id=self.product_id.id or False, report_view=self.report_view,
                            show_cost=self.show_cost, filter_by=self.filter_by,
                            warehouse_locations=warehouse_locations or False, location_ids=self.location_ids.ids or False,
                            group_by_type=self.group_by_type,
                            search_default_groupby_location_id=default_location_group,
                            search_default_groupby_warehouse_id=default_warehouse_group,
                            search_default_groupby_product_id=default_product_group),
        }
        return action

    @api.onchange('report_view')
    def onchange_report_view(self):
        self.product_id = False
        self.show_cost = False
        self.group_by_type = False

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        if self.filter_by == 'warehouse':
            self.location_ids = False
        elif self.filter_by == 'location':
            self.warehouse_ids = False
        else:
            self.location_ids = False
            self.warehouse_ids = False
