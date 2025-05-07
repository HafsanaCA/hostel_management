from email.policy import default

from odoo import models, fields, api

class PosSession(models.Model):
    _inherit = 'pos.session'

    max_discount_amount = fields.Float(compute='_compute_max_discount_amount', store=True)

    @api.depends('config_id')
    def _compute_max_discount_amount(self):
        config_param = self.env['ir.config_parameter'].sudo()
        max_discount = config_param.get_param('hostel_management.max_discount_amount', default='0.0')
        for session in self:
            session.max_discount_amount = float(max_discount)