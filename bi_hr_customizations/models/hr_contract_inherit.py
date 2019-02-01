# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    register_date = fields.Date(string='Start Date')
    # allowances
    transportation_allowed = fields.Boolean(string='Transportation Allowed')
    transportation = fields.Float(string='Transportation')
    transportation_amount = fields.Float(string='Transportation Amount', compute='get_transportation_amount')
    transportation_type = fields.Selection([('amount', 'Amount'), ('percentage', 'Percentage')],
                                           string='Transportation Type', )
    food_amount = fields.Float(string='Food Amount', )
    mobile_amount = fields.Float(string='Mobile Amount', )
    petrol_amount = fields.Float(string='Petrol Amount', )
    out_source_amount = fields.Float(string='Out Source Fees', )
    other_fixed_allowances_amount = fields.Float(string='Other Fixed Allowances', )
    tickets_amount = fields.Monetary(string='Tickets', )
    medical_insurance = fields.Monetary(string='Medical Insurance', )
    visa_fees = fields.Monetary(string='Visa Fees', )
    number_of_serviced_days = fields.Float(string='Number Of Serviced Days', compute='get_serviced_info',
                                           digits=(16, 3))
    number_of_serviced_years = fields.Float(string='Number Of Serviced Years', compute='get_serviced_info',
                                            digits=(16, 3))

    @api.multi
    @api.depends('date_start')
    def get_serviced_info(self):
        for rec in self:
            if rec.date_start:
                today = fields.datetime.now().date()
                start_date = fields.Datetime.from_string(rec.date_start).date()
                rec.number_of_serviced_days = (today - start_date).days
                rec.number_of_serviced_years = rec.number_of_serviced_days / 365

    @api.multi
    @api.constrains('transportation', )
    def check_transportation_percentage(self):
        for rec in self:
            if rec.transportation_type == 'percentage':
                if rec.transportation <= 0:
                    raise ValidationError("Transportation percentage should be greater than zero!")

                if rec.transportation >= 100:
                    raise ValidationError("Transportation percentage should be less than 100% !!")

    @api.multi
    @api.depends('wage', 'transportation_type')
    def get_transportation_amount(self):
        for rec in self:
            if rec.wage and rec.transportation_type:
                if rec.transportation_type == 'percentage':
                    if rec.wage and rec.transportation:
                        rec.transportation_amount = (rec.wage * rec.transportation) / 100
                elif rec.transportation_type == 'amount':
                    rec.transportation_amount = rec.transportation

    @api.onchange('transportation_type')
    def clear_transportation_value(self):
        for rec in self:
            rec.transportation = 0
