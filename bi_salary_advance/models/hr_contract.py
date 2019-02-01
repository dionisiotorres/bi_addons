# -*- coding: utf-8 -*-
from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    max_percent = fields.Integer(string='Max.Salary Advance Percentage')
