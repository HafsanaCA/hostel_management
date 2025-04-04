# -*- coding: utf-8 -*-
from odoo import models, fields


class LeaveRequest(models.Model):
    _name = 'leave.request'
    _description = 'Leave Request'
    _rec_name = 'student_id'

    arrival_date = fields.Date(string='Arrival Date')
    leave_date = fields.Date(string='Leave Date')
    status = fields.Selection(selection=[('new', 'New'), ('approved', 'Approved')], required=True, tracking=True,
                              default='new', readonly=True)
    student_id = fields.Many2one("student.information", string="Student", required=True)
    company_id = fields.Many2one('res.company', copy=False, string="Company",
                                 default=lambda self: self.env.user.company_id.id)

    def action_approved(self):
        """Changes the state of new leave requests to approved state"""
        self.write({'status': "approved"})

        room = self.student_id.room_id

        if room:
            other_students_in_room = room.student_ids.filtered(
                lambda s: s.active and s.id != self.student_id.id
            )

            if other_students_in_room == 0:
                self.env['cleaning.service'].create([{'room_id': room.id, }])
                room.state = 'cleaning'

