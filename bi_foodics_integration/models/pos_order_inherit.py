# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.tools.profiler import profile
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    hid = fields.Char(string='HID', copy=False)

    @api.constrains('hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid:
                if self.env['pos.order'].search_count([('hid', '=', rec.hid)]) > 1:
                    raise ValidationError(_('This HID already exists.'))


    # inherit to set entry date to session start date
    def _prepare_bank_statement_line_payment_values(self, data):
        args = super(PosOrderInherit, self)._prepare_bank_statement_line_payment_values(data)
        args.update({
            'date': self.session_id.start_at.date()
        })
        return args

    # process order method for orders that come from foodics, like standard but without session write
    @api.model
    def _process_order_new(self, pos_order):
        pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            pos_order['pos_session_id'] = self._get_valid_session(pos_order).id
        order = self.create(self._order_fields(pos_order))
        prec_acc = order.pricelist_id.currency_id.decimal_places
        journal_ids = set()
        for payments in pos_order['statement_ids']:
            if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
                order.add_payment(self._payment_fields(payments[2]))
            journal_ids.add(payments[2]['journal_id'])

        # if pos_session.sequence_number <= pos_order['sequence_number']:
        #     pos_session.write({'sequence_number': pos_order['sequence_number'] + 1})
        #     pos_session.refresh()

        if not float_is_zero(pos_order['amount_return'], prec_acc):
            cash_journal_id = pos_session.cash_journal_id.id
            if not cash_journal_id:
                # Select for change one of the cash journals used in this
                # payment
                cash_journal = self.env['account.journal'].search([
                    ('type', '=', 'cash'),
                    ('id', 'in', list(journal_ids)),
                ], limit=1)
                if not cash_journal:
                    # If none, select for change one of the cash journals of the POS
                    # This is used for example when a customer pays by credit card
                    # an amount higher than total amount of the order and gets cash back
                    cash_journal = [statement.journal_id for statement in pos_session.statement_ids if statement.journal_id.type == 'cash']
                    if not cash_journal:
                        raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
                cash_journal_id = cash_journal[0].id
            order.add_payment({
                'amount': -pos_order['amount_return'],
                'payment_date': fields.Date.context_today(self),
                'payment_name': _('return'),
                'journal': cash_journal_id,
            })
        return order

    @api.model
    def create_from_ui_new(self, orders):
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order_new(order)
            order_ids.append(pos_order.id)

            try:
                pos_order.action_pos_order_paid_new()
            except psycopg2.OperationalError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                pos_order.action_pos_order_invoice()
                pos_order.invoice_id.sudo().action_invoice_open()
                pos_order.account_move = pos_order.invoice_id.move_id
        return order_ids

    # remove create picking
    @api.multi
    def action_pos_order_paid_new(self):
        for rec in self:
            if not rec.test_paid():
                raise UserError(_("Order is not paid."))
            rec.write({'state': 'paid'})
            # return rec.create_picking()


class PosOrderLineInherit(models.Model):
    _inherit = 'pos.order.line'

    hid = fields.Char(string='HID', copy=False)

    @api.constrains('hid')
    def check_unique_hid(self):
        for rec in self:
            if rec.hid:
                if self.env['pos.order.line'].search_count([('hid', '=', rec.hid)]) > 1:
                    raise ValidationError(_('This HID already exists.'))