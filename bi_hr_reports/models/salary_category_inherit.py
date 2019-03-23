# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrSalaryCategInh(models.Model):
    _inherit = 'hr.salary.rule.category'

    sequence = fields.Integer(string='Sequence', default=1, copy=False)
    view_in_report = fields.Boolean(string='View In Payslip Report', default=True)
