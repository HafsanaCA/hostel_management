# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    bom_product_ids = fields.Many2many('product.product', compute="_compute_bom_product_ids",
                                       help="List of Products used in the BoM, used to filter the list of products in "
                                            "the subcontracting portal view")
