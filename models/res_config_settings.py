# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bom_product_ids = fields.Many2many('product.product', string='BoM Products for Cart',
                                       help="List of Products used in the BoM, used to filter the list of products in "
                                            "the subcontracting portal view")
    max_discount_amount = fields.Float(string="Maximum Discount Limit", help="Global discount limit for POS sessions.")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env['ir.config_parameter'].sudo()
        bom_products = icp.get_param('hostel_management.bom_product_ids', default='[]')
        max_discount = icp.get_param('hostel_management.max_discount_amount', default='0.0')
        res.update(
            {'bom_product_ids': [(6, 0, literal_eval(bom_products))], 'max_discount_amount': float(max_discount), })
        return res

    def set_values(self):
        super().set_values()
        icp = self.env['ir.config_parameter'].sudo()
        icp.set_param('hostel_management.bom_product_ids', self.bom_product_ids.ids)
        icp.set_param('hostel_management.max_discount_amount', self.max_discount_amount)
