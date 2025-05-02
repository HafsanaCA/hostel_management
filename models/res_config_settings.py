# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bom_product_ids = fields.Many2many('product.product', string='BoM Products for Cart',
                                       help="List of Products used in the BoM, used to filter the list of products in "
                                            "the subcontracting portal view")

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env['ir.config_parameter'].sudo()
        bom_products = icp.get_param('hostel_management.bom_product_ids', default='[]')
        res.update({'bom_product_ids': [(6, 0, literal_eval(bom_products))]})
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('hostel_management.bom_product_ids',self.bom_product_ids.ids)