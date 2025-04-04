# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HostelFacilities(models.Model):
    _name = 'hostel.facility'
    _description = 'Hostel Facility'

    name = fields.Char(string='Name', required=True)
    company_id = fields.Many2one('res.company', copy=False, string="Company",)
    currency_id = fields.Many2one('res.currency', string="Currency", related='company_id.currency_id')
    charge = fields.Monetary(string='Charge', required=True, default=1)

    @api.constrains('charge')
    def _check_charge(self):
        """ For validating charges of facilities, if value is zero or negative, it raises a validation error."""
        if self.charge <= 0:
            raise ValidationError("Charge cannot be zero or negative!")
