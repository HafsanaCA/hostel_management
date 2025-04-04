# -*- coding: utf-8 -*-
from odoo import models, fields


class RentalProduct(models.Model):
    _name = 'rental.product'
    _description = 'Rental Product'

    name = fields.Char("Product")
    price = fields.Monetary("Price")
    company_id = fields.Many2one('res.company', copy=False, string="Company", )
    currency_id = fields.Many2one('res.currency', string="Currency", related='company_id.currency_id')

