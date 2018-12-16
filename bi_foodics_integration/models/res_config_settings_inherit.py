# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    foodics_base_url = fields.Char('Foodics base URL')
    foodics_secret = fields.Char('Foodics secret')

    @api.model
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        res.update(
            foodics_base_url= self.env['ir.config_parameter'].sudo().get_param('bi_foodics_integration.foodics_base_url'),
            foodics_secret= self.env['ir.config_parameter'].sudo().get_param('bi_foodics_integration.foodics_secret'),
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('bi_foodics_integration.foodics_base_url', self.foodics_base_url)
        self.env['ir.config_parameter'].sudo().set_param('bi_foodics_integration.foodics_secret', self.foodics_secret)