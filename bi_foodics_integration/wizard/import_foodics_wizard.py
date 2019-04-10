# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ImportFoodicsWizard(models.TransientModel):
    _name = 'import.foodics.wizard'

    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    pos_id = fields.Many2one('pos.config', string="POS")
    use_date_range = fields.Boolean('Use Date Range?')
    date = fields.Date(string='Start Date', required=True, default=_get_default_date)
    end_date = fields.Date(string='End Date', required=True, default=_get_default_date)


    @api.multi
    def import_foodics_data(self):
        for rec in self:
            if rec.pos_id:
                rec.pos_id.import_foodics_data(rec.date, rec.end_date)
            else:
                active_pos_ids = self.env.context.get('active_ids', [])
                for pos in self.env['pos.config'].search([('id', 'in', active_pos_ids), ('current_session_id', '=', False), ('pos_session_username', '=', False)]):
                    pos.import_foodics_data(rec.date, rec.end_date)

    @api.constrains('use_date_range','date','end_date')
    def _constrain_dates(self):
        for rec in self:
            if rec.use_date_range and rec.end_date < rec.date:
                raise ValidationError(_('End date must be greater than start date!'))

    @api.onchange('use_date_range','date','end_date')
    def onchange_use_date_range(self):
        for rec in self:
            if not rec.use_date_range:
                if rec.date:
                    rec.end_date = rec.date
                else:
                    rec.end_date = False

class ImportFoodicsPerSessionWizard(models.TransientModel):
    _name = 'import.foodics.per.session.wizard'

    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    pos_id = fields.Many2one('pos.config', string="POS")
    use_date_range = fields.Boolean('Use Date Range?')
    date = fields.Date(string='Start Date', required=True, default=_get_default_date)
    end_date = fields.Date(string='End Date', required=True, default=_get_default_date)

    @api.multi
    def import_foodics_data_per_session(self):
        for rec in self:
            if rec.pos_id:
                rec.pos_id.import_foodics_data_per_session(rec.date, rec.end_date)

    @api.constrains('use_date_range','date','end_date')
    def _constrain_dates(self):
        for rec in self:
            if rec.use_date_range and rec.end_date < rec.date:
                raise ValidationError(_('End date must be greater than start date!'))

    @api.onchange('use_date_range','date','end_date')
    def onchange_use_date_range(self):
        for rec in self:
            if not rec.use_date_range:
                if rec.date:
                    rec.end_date = rec.date
                else:
                    rec.end_date = False
