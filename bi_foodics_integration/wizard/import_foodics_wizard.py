# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ImportFoodicsWizard(models.TransientModel):
    _name = 'import.foodics.wizard'

    def _get_default_date(self):
        return fields.Date.from_string(fields.Date.today())

    pos_id = fields.Many2one('pos.config', string="POS")
    date = fields.Date(string='Date', required=True, default=_get_default_date)


    @api.multi
    def import_foodics_data(self):
        for rec in self:
            if rec.pos_id:
                rec.pos_id.import_foodics_data(rec.date)
            else:
                active_pos_ids = self.env.context.get('active_ids', [])
                for pos in self.env['pos.config'].search([('id', 'in', active_pos_ids), ('current_session_id', '=', False), ('pos_session_username', '=', False)]):
                    pos.import_foodics_data(rec.date)