# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StudentRegistration(models.Model):
    _name = 'student.registration'
    _description = 'Student Registration'

    name = fields.Char(string='Name')
    email = fields.Char(string='Email')
