# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class StudentRegistration(models.Model):
    _name = 'student.registration'
    _description = 'Student Registration'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    dob = fields.Date(string='Date of Birth', required=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True)
    receive_mail = fields.Boolean(string='Receive Mails', default=False)
    room_id = fields.Many2one('room.management', string='Room')

    @api.depends('dob')
    def _compute_age(self):
        if self.dob:
            self.age = relativedelta(date.today(), self.dob).years
        else:
            self.age = 0

