# -*- coding: utf-8 -*-
import json
import io
import xlsxwriter
from odoo import models,fields
from odoo.http import request


class StudentWizard(models.TransientModel):
    _name = 'student.wizard'
    _description = 'Student wizard'

    room_id = fields.Many2one('room.management', string='Room')
    student_id = fields.Many2one('student.information', string='Student')

    def action_print_report(self):
        data = {
            'student_id': self.student_id.id,
            'room_id' : self.room_id.id
        }
        return self.env.ref('hostel_management.student_report_pdf').report_action(self, data=data)

    def action_print_xlsx(self):
        data = {
            'model_id': self.id,
            'student_id': self.student_id.id,
            'room_id': self.room_id.id,
        }
        return {
            'type': 'ir.actions.report',
            'data': {
                'model': 'student.wizard',
                'options': json.dumps(data),
                'output_format': 'xlsx',
                'report_name': 'Student Excel Report',
            },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        room = request.env['room.management'].browse(data.get('room_id'))
        student = request.env['student.information'].browse(data.get('student_id'))

        print("Student ID:", data.get('student_id'))
        print("Student Record:", student)
        print("Student Name:", student.name)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'font_size': 11, 'align': 'center'})
        head_format = workbook.add_format({'bold': True, 'font_size': 20, 'align': 'center'})
        text_format = workbook.add_format({'font_size': 10, 'align':'center'})

        sheet.merge_range('H2:M3', 'STUDENT REPORT', head_format)

        # if room:
        sheet.merge_range('A7:B7', 'Room ', cell_format)
        sheet.write('C7', room.name, text_format)

        # if student:
        sheet.merge_range('A6:B6', 'Student ', cell_format)
        sheet.write('C6', student.name, text_format)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
