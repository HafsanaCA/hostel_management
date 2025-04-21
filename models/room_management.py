# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class RoomManagement(models.Model):
    _name = 'room.management'
    _description = 'Room Management'
    _inherit = ['mail.thread']

    name = fields.Char(string="Room Number", default=lambda self: _('New'), copy=False, readonly=True, tracking=True)
    room_type = fields.Selection(
        [('dormitory', 'Dormitory'), ('private', 'Private'), ('twin', 'Twin'), ('double', 'Double'), ],
        string="Room Type", required=True, tracking=True)
    company_id = fields.Many2one('res.company', copy=False, string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency", related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    beds = fields.Integer(string="Beds", required=True, tracking=True)
    rent = fields.Monetary(string="Rent", required=True, tracking=True)
    state = fields.Selection(
        selection=[('empty', 'Empty'), ('partial', 'Partial'), ('cleaning', 'Cleaning'), ('full', 'Full')],
        string='Status', required=True, tracking=True, default='empty', readonly=True, compute='_compute_state',
        store=True)
    occupied_beds = fields.Integer(string="Occupied Beds", default=0)
    facility_ids = fields.Many2many(comodel_name='hostel.facility', string='Facilities')
    student_ids = fields.One2many('student.information', 'room_id', string="Students")
    invoice_count = fields.Integer(string="Invoice Count")
    cleaning_ids = fields.One2many('cleaning.service', 'room_id', string="Cleaning Services")
    total_rent = fields.Monetary(string='Total Rent', compute='_compute_total_rent', store=True)
    pending_amount = fields.Monetary(string='Pending Amount', compute='_compute_pending_amount', store=True)

    @api.depends('occupied_beds', 'beds')
    def _compute_state(self):
        """Computes the room state corresponding to the number of occupied beds in room"""
        for room in self:
            if room.occupied_beds == 0:
                room.state = 'empty'
            elif room.occupied_beds < room.beds:
                room.state = 'partial'
            else:
                room.state = 'full'

    @api.depends('rent', 'facility_ids')
    def _compute_total_rent(self):
        """It calculates the total rent of the room by summing up the rent amount and total facilities amount"""
        for room in self:
            room.total_rent = room.rent + sum(room.facility_ids.mapped('charge'))

    @api.depends('student_ids.invoice_ids.amount_residual', 'student_ids.invoice_ids.state')
    def _compute_pending_amount(self):
        """It calculates the pending amount left in room which arises from the unpaid invoices from students"""
        for room in self:
            pending_invoices = self.env['account.move'].search([
                ('student_id', 'in', room.student_ids.ids),
                ('state', 'not in', ['paid', 'cancel', 'draft'])
            ])
            room.pending_amount = sum(pending_invoices.mapped('amount_residual'))

    def action_partial(self):
        self.write({'state': "partial"})

    def action_full(self):
        self.write({'state': "full"})

    def action_create_monthly_invoice(self):
        """Creates monthly invoices for students at the start of each month for the separate students in the room"""
        self.ensure_one()

        product = self.env.ref('hostel_management.product_rent_service')
        if not product:
            raise UserError("Rent product not found")

        invoices = []
        today = date.today()
        start_of_month = today.replace(day=1)

        for student in self.student_ids:
            existing_invoice = self.env['account.move'].search([('student_id', '=', student.id),
                ('move_type', '=', 'out_invoice'),('invoice_date', '>=', start_of_month),], limit=1)

            if existing_invoice:
                raise UserError("All the students in this room hae been invoiced for this month")

            invoice_vals = [{
                'partner_id': student.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_date': today,
                'currency_id': self.currency_id.id,
                'student_id': student.id,
                'invoice_line_ids': [
                     fields.Command.create({
                        'product_id': product.id,
                        'name': "Rent for " + str(self.name) + " - " + str(student.name),
                        'quantity': 1,
                        'price_unit': self.total_rent + product.lst_price,
                    }),
                ]
            }]
            invoice = self.env['account.move'].create(invoice_vals)
            invoices.append(invoice.id)

        return {
            'type' : 'ir.actions.act_window',
            'name' : 'Created Invoices',
            'res_model' : 'account.move',
            'view_mode' : 'list,form',
            'domain' : [('id', 'in', invoices)]
        }

    @api.model_create_multi
    def create(self, vals_list):
        """ Creates sequence number for rooms"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (self.env['ir.sequence'].next_by_code('room.management'))
        return super().create(vals_list)
