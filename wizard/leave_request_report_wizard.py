# -*- coding: utf-8 -*-
from odoo import models, fields


class LeaveRequestReport(models.TransientModel):
    _name = 'leave.request.report'
    _description = 'Leave Request Report'

    student_id = fields.Many2one('student.information', string='Student')
    room_id = fields.Many2one('room.management', string='Room')
    arrival_date = fields.Date(string='Arrival Date')
    leave_date = fields.Date(string='Leave Date')

    def action_print_leave_report(self):
        data = {
            'student_id': self.student_id.id if self.student_id else None,
            'room_id': self.room_id.id if self.room_id else None,
            'arrival_date': self.arrival_date.isoformat() if self.arrival_date else None,
            'leave_date': self.leave_date.isoformat() if self.leave_date else None,
        }
        return self.env.ref('hostel_management.student_leave_report_pdf').report_action(self, data=data)
