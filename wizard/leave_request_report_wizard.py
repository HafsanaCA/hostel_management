# -*- coding: utf-8 -*-
import json
import io
import xlsxwriter
from odoo import models,fields
from odoo.http import request


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

    def action_print_leave_xlsx(self):
        data = {
            'student_id': self.student_id.id if self.student_id else None,
            'room_id': self.room_id.id if self.room_id else None,
            'arrival_date': self.arrival_date.isoformat() if self.arrival_date else None,
            'leave_date': self.leave_date.isoformat() if self.leave_date else None,
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'leave.request.report',
                'options': json.dumps(data),
                'output_format': 'xlsx',
                'report_name': 'Leave Request Report',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        student_id = data.get('student_id')
        room_id = data.get('room_id')
        arrival_date = data.get('arrival_date')
        leave_date = data.get('leave_date')

        query = """
                SELECT row_number() OVER() AS sl_no,
                       s.name AS student_name, 
                       r.name AS room_name, 
                       l.leave_date, 
                       l.arrival_date,
                       (l.leave_date - l.arrival_date) AS duration
                FROM leave_request l
                JOIN student_information s ON s.id = l.student_id
                JOIN room_management r ON r.id = s.room_id
                WHERE
                    (%(student_id)s IS NULL OR s.id = %(student_id)s) 
                    AND (%(room_id)s IS NULL OR r.id = %(room_id)s)
                    AND (%(arrival_date)s IS NULL OR l.arrival_date >= %(arrival_date)s)
                    AND (%(leave_date)s IS NULL OR l.leave_date <= %(leave_date)s)
            """
        request.env.cr.execute(query, {
            'student_id': student_id,
            'room_id': room_id,
            'arrival_date': arrival_date,
            'leave_date': leave_date,
        })

        results = request.env.cr.dictfetchall()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        head_format = workbook.add_format({'bold': True, 'font_size': 22, 'align': 'center'})
        cell_format = workbook.add_format({'font_size': 10, 'align': 'center', 'bg_color': '#f2f2f2', 'bold': True,
                                           'border': 1})
        text_format = workbook.add_format({'font_size': 10, 'align': 'center', 'border': 1})

        sheet.merge_range('F2:I3', 'STUDENTS LEAVE REQUEST REPORT', head_format)

        row = 5
        if student_id:
            student = request.env['student.information'].browse(student_id)
            if student.exists():
                sheet.write(row, 4, "Student",cell_format)
                sheet.write(row, 5, student.name ,text_format)
                row += 1
        if room_id:
            room = request.env['room.management'].browse(room_id)
            if room.exists():
                sheet.write(row, 4, "Room", cell_format)
                sheet.write(row, 5, room.name, text_format)
                row += 1
        if arrival_date:
            sheet.write(row, 4, "From Date", cell_format)
            sheet.write(row, 5, arrival_date, text_format)
            row += 1
        if leave_date:
            sheet.write(row, 4, "To Date", cell_format)
            sheet.write(row, 5, leave_date, text_format)
            row += 1
        row += 1

        columns = [('Sl.No', 15)]
        if not room_id and not student_id:
            columns.append(('Room', 20))
        if not student_id:
            columns.append(('Student', 20))
        columns += [('Start Date', 15), ('End Date', 15), ('Duration', 15)]

        for col_id, (header, width) in enumerate(columns):
            sheet.set_column(col_id + 4, col_id + 4, width)
            sheet.write(row,col_id + 4, header, cell_format)
        row += 1

        for rec in results:
            col = 4
            sheet.write(row, col, rec.get('sl_no'), text_format)
            col += 1
            if not room_id and not student_id:
                sheet.write(row, col, rec.get('room_name'), text_format)
                col += 1
            if not student_id:
                sheet.write(row, col, rec.get('student_name'), text_format)
                col += 1
            sheet.write(row, col, str(rec.get('arrival_date')), text_format)
            col += 1
            sheet.write(row, col, str(rec.get('leave_date')), text_format)
            col += 1
            sheet.write(row, col, rec.get('duration'), text_format)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
