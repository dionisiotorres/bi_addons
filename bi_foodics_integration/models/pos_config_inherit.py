# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import uuid4
import json
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PosBranch(models.Model):
    _name = 'pos.branch'

    name = fields.Char(string='Name', required=True)
    hid = fields.Char(string='HID', required=True, copy=False)
    responsible_id = fields.Many2one('res.users', string='Responsible', required=True)

    @api.constrains('hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid:
                if self.env['pos.branch'].search_count([('hid', '=', rec.hid)]) > 1:
                    raise ValidationError(_('This HID already exists.'))


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    pos_branch_id = fields.Many2one('pos.branch', string='Branch')


    @api.model
    def get_token(self, foodics_base_url, foodics_secret):
        request_url = foodics_base_url + '/api/v2/token'
        data = {
            "secret": foodics_secret,
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.post(request_url, data=json.dumps(data), headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'token' in content:
                token = content['token']
            else:
                token = False
        except:
            token = False
        return token

    @api.model
    def get_business_hid(self, foodics_base_url, token):
        request_url = foodics_base_url + '/api/v2/businesses'
        headers = {
            'Authorization': ('Bearer %s' % token),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        try:
            req = requests.get(request_url, headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'businesses' in content and len(content['businesses']) and 'hid' in content['businesses'][0]:
                business_hid = content['businesses'][0]['hid']
            else:
                business_hid = False
        except:
            business_hid = False
        return business_hid

    @api.model
    def get_headers(self, foodics_base_url, foodics_secret):
        token = self.get_token(foodics_base_url, foodics_secret)
        if token:
            business_hid = self.get_business_hid(foodics_base_url, token)
            if business_hid:
                headers = {
                    'Authorization': ('Bearer %s' % token),
                    'X-business': business_hid,
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                return headers
            else:
                raise ValidationError(_('No Business HID found!'))
        else:
            raise ValidationError(_('Failed to get token!'))

    @api.model
    def get_branches(self, foodics_base_url, headers):
        request_url = foodics_base_url + '/api/v2/branches'
        try:
            req = requests.get(request_url, headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'branches' in content:
                branches = content['branches']
            else:
                branches = False
        except:
            branches = False
        return branches

    @api.model
    def get_orders(self, foodics_base_url, headers, business_date, branch_hid):
        request_url = foodics_base_url + "/api/v2/orders?filters[business_date]=%s&filters[branch_hid]=%s"%(business_date, branch_hid)
        try:
            req = requests.get(request_url, headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'orders' in content:
                orders = content['orders']
            else:
                orders = False
        except:
            orders = False
        return orders

    @api.model
    def get_orders_by_hid(self, foodics_base_url, headers, order_hid):
        request_url = foodics_base_url + "/api/v2/orders/%s" % (order_hid)
        try:
            req = requests.get(request_url, headers=headers)
            req.raise_for_status()
            content = req.json()
            if 'order' in content:
                order = content['order']
            else:
                order = False
        except:
            order = False
        return order

    @api.model
    def get_product_by_hid(self, hid, size_hid=False):
        if size_hid:
            domain = [('hid', '=', hid), ('size_hid', '=', size_hid)]
        else:
            domain = [('hid', '=', hid)]
        product = self.env['product.product'].search(domain, limit=1)
        if product:
            return product
        else:
            if size_hid:
                raise ValidationError(_('There is no product found with the hid %s and size hid %s')%(hid, size_hid))
            else:
                raise ValidationError(_('There is no product found with the hid %s') % (hid))

    @api.model
    def get_payment_method_by_hid(self, hid):
        journal = self.env['account.journal'].search([('hid', '=', hid)], limit=1)
        if journal:
            return journal
        else:
            raise ValidationError(_('There is no payment method found with the hid %s') % (hid))

    @api.model
    def get_pos_related_payment_method_by_hid(self, hid, pos_session):
        pos_id = pos_session.config_id
        journal = False
        for j in pos_id.journal_ids:
            if j.hid == hid:
                journal = j
                break
        if journal:
            return journal
        else:
            raise ValidationError(_('POS has no payment method with the hid %s') % (hid))

    @api.model
    def get_user_by_hid(self, hid):
        user = self.env['res.users'].search([('hid', '=', hid)], limit=1)
        if user:
            return user
        else:
            raise ValidationError(_('There is no user found with the hid %s') % (hid))

    @api.model
    def get_partner_by_hid(self, hid):
        partner = self.env['res.partner'].search([('hid', '=', hid)], limit=1)
        if partner:
            return partner
        else:
            raise ValidationError(_('There is no partner found with the hid %s') % (hid))

    @api.model
    def get_tax_by_hid(self, hid):
        tax = self.env['account.tax'].search([('hid', '=', hid)], limit=1)
        if tax:
            return tax
        else:
            raise ValidationError(_('There is no Tax found with the hid %s') % (hid))

    @api.model
    def get_statment(self, journal, current_session):
        statments = current_session.statement_ids
        statment = False
        for st in statments:
            if st.journal_id == journal:
                statment = st
                break
        if statment:
            return statment
        else:
            raise ValidationError(_('There is no statment found with the journal %s') % (journal.name))

    def _prepare_api_order_lines(self, lines, taxes):
        p_lines = []
        for line in lines:
            if 'product_size_hid' in line and line['product_size_hid']:
                product_size_hid = line['product_size_hid']
            else:
                product_size_hid = False
            product = self.get_product_by_hid(line['product_hid'], product_size_hid)
            p_lines.append([0, 0, {
                    'discount': line['discount_amount'],
                    'pack_lot_ids': [],
                    'price_unit': line['displayable_final_price']/line['quantity'] if line['quantity'] else 0.0,
                    'product_id': product.id,
                    'price_subtotal': line['final_price'],
                    'price_subtotal_incl': line['displayable_final_price'],
                    'qty': line['quantity'],
                    'tax_ids': [(6, 0, taxes)] if taxes else False
                }
            ])
        return p_lines

    def _prepare_api_statements(self, lines, current_session):
        s_lines = []
        for line in lines:
            journal = self.get_pos_related_payment_method_by_hid(line['payment_method']['hid'], current_session)
            if not journal.default_debit_account_id:
                raise ValidationError(_('Please define the default debit/credit account for journal %s')%(journal.name))
            s_lines.append([0, 0, {
                    'account_id': journal.default_debit_account_id.id,
                    'journal_id': journal.id,
                    'name': line['actual_date'],
                    'amount': line['amount'],
                    'statement_id': self.get_statment(journal, current_session)
                }
            ])
        return s_lines

    @api.model
    def _update_orders_amount_all(self, order_ids):
        orders = self.env['pos.order'].browse(order_ids)
        for order in orders:
            self._update_order_lines_amount_all(order.lines)
            currency = order.pricelist_id.currency_id
            order.amount_paid = sum(payment.amount for payment in order.statement_ids)
            order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.statement_ids)
            order.amount_tax = currency.round(
                sum(order._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            order.amount_total = order.amount_tax + amount_untaxed

    @api.model
    def _update_order_lines_amount_all(self, lines):
        for line in lines:
            res = line._compute_amount_line_all()
            line.write(res)

    @api.model
    def _prepare_api_order(self, order, current_session):
        customer = False
        user = current_session.config_id.pos_branch_id and current_session.config_id.pos_branch_id.responsible_id

        # to set cashier from api response
        # if 'cashier' in order and order['cashier']['hid']:
        #     user = self.get_user_by_hid(order['cashier']['hid'])

        if 'customer' in order and order['customer'] and order['customer']['hid']:
            customer = self.get_partner_by_hid(order['customer']['hid'])

        amount_paid = 0.0
        if 'payments' in order:
            for payment in order['payments']:
                amount_paid += payment['amount']

        taxes = []
        if 'taxes' in order and order['taxes']:
            for tx in order['taxes']:
                tax = self.get_tax_by_hid(tx['hid'])
                taxes.append(tax.id)

        return {
            'data':
                {
                    'amount_paid': amount_paid,
                    'amount_return': 0,
                    'amount_tax': order['total_tax'],
                    'amount_total': order['final_price'],
                    'date_order': order['closed_at'],
                    'fiscal_position_id': False,
                    'pricelist_id': self.available_pricelist_ids[0].id,
                    'lines': self._prepare_api_order_lines(order['products'], taxes),
                    'name': order['reference'],
                    'partner_id': customer.id if customer else False,
                    'pos_session_id': current_session.id,
                    'sequence_number': order['number'],
                    'creation_date': order['closed_at'],
                    'statement_ids': self._prepare_api_statements(order['payments'], current_session),
                    'uid': order['reference'],
                    'user_id': user.id if user else self.env.uid
                },
            'id': order['reference'],
            'to_invoice': False
        }

    @api.multi
    def import_foodics_data(self, date):
        self.ensure_one()

        foodics_base_url = self.env['ir.config_parameter'].sudo().get_param('bi_foodics_integration.foodics_base_url')
        foodics_secret = self.env['ir.config_parameter'].sudo().get_param('bi_foodics_integration.foodics_secret')

        if not foodics_base_url or not foodics_secret:
            raise ValidationError(_('Please configure Foodics base URL and secret.'))

        if not self.pos_branch_id:
            raise ValidationError(_('Please set the branch in the pos.'))

        business_date = date.strftime('%Y-%m-%d')

        headers = self.get_headers(foodics_base_url, foodics_secret)
        orders = self.get_orders(foodics_base_url, headers, business_date, self.pos_branch_id.hid)

        if not orders:
            return
            # raise ValidationError(_('No orders found.'))

        if not self.current_session_id:
            self.current_session_id = self.env['pos.session'].create({
                'user_id': self.env.uid,
                'config_id': self.id
            })

        pos_orders = []
        for order in orders:
            if 'payments' in order and order['payments']:
                pos_order = self._prepare_api_order(order, self.current_session_id)
                pos_orders.append(pos_order)

        created_order_ids = self.env['pos.order'].create_from_ui(pos_orders)
        self._update_orders_amount_all(created_order_ids)

        # close and validate session
        self.current_session_id.action_pos_session_closing_control()