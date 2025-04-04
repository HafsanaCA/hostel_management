# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class StudentInformation(models.Model):
    _name = 'student.information'
    _description = 'Student Information'

    name = fields.Char(tracking=True, readonly=False,required=True)
    student = fields.Char(default=lambda self: _('New'), copy=False, readonly=True, tracking=True)
    dob = fields.Date(string="Date of Birth", tracking=True, default=fields.Datetime.now())
    email = fields.Char(string="Email", tracking=True)
    image = fields.Binary()
    receive_mail = fields.Boolean(string="Receive Mails", tracking=True)
    room_id = fields.Many2one('room.management', string="Room", tracking=True, readonly=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    company_id = fields.Many2one('res.company', copy=False, string="Company")
    age = fields.Integer(string="Age")
    room_type = fields.Selection(
        [('dormitory', 'Dormitory'), ('private', 'Private'), ('twin', 'Twin'), ('double', 'Double'), ],
        string="Room Type", tracking=True)
    occupied_beds = fields.Integer(string="Occupied Beds", default=0)
    partner_id = fields.Many2one('res.partner', ondelete='restrict', auto_join=True, required=False, string='Partner',
                                 help='Partner-related data of the student', readonly=True)
    leave_request_ids = fields.One2many('leave.request', 'student_id', string="Leave Requests",
                                        readonly=True)
    invoice_count = fields.Integer(string="Invoice Count", compute="_compute_invoice_count")
    currency_id = fields.Many2one('res.currency', string="Currency", related='company_id.currency_id',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    monthly_amount = fields.Monetary(string="Monthly Amount", compute="_compute_monthly_amount", store=True)
    invoice_status = fields.Selection([('pending', 'Pending'), ('done', 'Done')],string="Invoice Status",
                                      compute='_compute_invoice_status',store=True)
    user_id = fields.Many2one('res.users', string='User')
    active = fields.Boolean(string="Active", default=True)
    invoice_ids = fields.One2many('account.move', 'student_id', string="Invoices")


    @api.model_create_multi
    def create(self, vals_list):
        """Generates sequence number for students, along with the automatic creation of partner when a student record is
        created"""
        for vals in vals_list:
            if vals.get('student', _('New')) == _('New'):
                vals['student'] = (self.env['ir.sequence'].next_by_code('student.information'))

            partner_vals = {
                'name': vals.get('name'),
                'email': vals.get('email'),
                'street': vals.get('street'),
                'street2': vals.get('street2'),
                'zip': vals.get('zip'),
                'city': vals.get('city'),
                'state_id': vals.get('state_id'),
                'country_id': vals.get('country_id'),
            }
            partner = self.env['res.partner'].create(partner_vals)
            vals['partner_id'] = partner.id

        return super().create(vals_list)

    @api.model
    def create_user_from_student(self):
        """Creates a user automatically when a student record is created"""
        user_vals = {
            'name': self.name,
            'login': self.email,
            'email': self.email,
        }
        user = self.env['res.users'].create(user_vals)
        self.user_id = user.id

    @api.onchange('dob')
    def _onchange_dob(self):
        """Calculates the age of the student from the date of birth of student"""
        if self.dob:
            self.age = relativedelta(date.today(), self.dob).years
        else:
            self.age = 0

    def action_allocate_room(self):
        """Allocates available rooms for students"""
        room = self.env["room.management"]

        available_room = room.search([('state', 'in', ['empty', 'partial']), ], limit=1, order="occupied_beds asc")
        if available_room and available_room.occupied_beds < available_room.beds:
            self.room_id = available_room.id
            self.room_id.write({'occupied_beds': self.room_id.occupied_beds + 1})
        else:
            raise UserError("No available rooms")

    def action_vacate_room(self):
        """Vacates students and archive them immediately"""
        room = self.room_id
        room.write({'occupied_beds': room.occupied_beds - 1})
        self.write({'room_id': False,'active': False})

        room._compute_state()
        if not room.student_ids:
            self.env['cleaning.service'].create([{'room_id': room.id}])
            room.state = 'cleaning'


    def _compute_invoice_count(self):
        """Calculates invoice generated for each student"""
        for student in self:
            student.invoice_count = self.env['account.move'].search_count([('student_id', '=', self.id)])

    def action_view_invoice(self):
        """It opens the appropriate views for opening the invoice"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('student_id', '=', self.id)],
        }

    @api.depends('room_id.total_rent')
    def _compute_monthly_amount(self):
        """It calculates the amount for each student associated with a room """
        for student in self:
            student.monthly_amount = student.room_id.total_rent if student.room_id else 0.0

    def unlink(self):
        """It deletes the related records associated with the student"""
        self.env['leave.request'].search([('student_id', 'in', self.ids)]).unlink()
        return super(StudentInformation, self).unlink()


    @api.depends('invoice_ids.state')
    def _compute_invoice_status(self):
        """It computes the invoice status by switching from new, pending an also done"""
        for student in self:
            pending_invoices = student.invoice_ids.filtered(lambda inv: inv.state not in ['posted', 'paid'])
            if pending_invoices:
                student.invoice_status = 'pending'
            else:
                student.invoice_status = 'done'
