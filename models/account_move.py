# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    student_id = fields.Many2one('student.information', string="Student")

    def action_post(self):
        """ Sends an email to the student when confirming an invoice"""
        res = super().action_post()

        if self.student_id.receive_mail:
            template = self.env.ref('hostel_management.email_template_invoice')
            template.send_mail(self.id, force_send=True)

        return res